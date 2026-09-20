"""
Rotas para Reports (Activity Statement PDF import)

Endpoints:
- POST /api/reports/upload   -> upload de 1+ PDFs, parse e insert nas 15 tabelas.
                                Retorna resumo de registos inseridos por tabela.
- GET  /api/reports/files    -> lista de ficheiros ja processados.
- GET  /api/reports/summary  -> contadores globais (nr ficheiros).
"""
import hashlib
import logging
from typing import List, Dict, Any

from fastapi import APIRouter, HTTPException, status, UploadFile, File

from db.supabase_client import get_db
from services.report_parser import parse_report

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/reports", tags=["reports"])

db = get_db()

# Ordem das 15 tabelas (para resumo consistente)
DATA_TABLES = [
    "invest_executed_trades",
    "invest_pending_orders",
    "invest_open_positions",
    "invest_transactions",
    "invest_dividends",
    "cfd_executed_trades",
    "cfd_pending_orders",
    "cfd_open_positions",
    "cfd_transactions",
    "cfd_dividend_adjustments",
    "cfd_overnight_interest",
    "crypto_executed_trades",
    "crypto_pending_orders",
    "crypto_open_positions",
    "crypto_transactions",
]


def _insert_rows(table: str, rows: List[Dict[str, Any]]) -> int:
    """Insere linhas em lote. Retorna nr inseridos."""
    if not rows:
        return 0
    inserted = 0
    # Supabase aceita insert em lote; partir em chunks p/ payloads grandes
    CHUNK = 500
    for i in range(0, len(rows), CHUNK):
        chunk = rows[i:i + CHUNK]
        resp = db.client.table(table).insert(chunk).execute()
        inserted += len(resp.data or [])
    return inserted


@router.post("/upload")
async def upload_reports(files: List[UploadFile] = File(...)) -> Dict[str, Any]:
    """
    Upload de 1+ ficheiros PDF (Activity Statements).
    Para cada ficheiro:
      1. Calcula hash (dedup); se ja importado, marca como 'skipped'.
      2. Cria registo em imported_files.
      3. Parse do PDF -> 15 tabelas.
      4. Insere registos com file_id.
      5. Atualiza status do ficheiro.
    Retorna resumo agregado + por ficheiro.
    """
    results = []
    grand_total = {t: 0 for t in DATA_TABLES}

    for upload in files:
        raw = await upload.read()
        file_hash = hashlib.sha256(raw).hexdigest()

        # Dedup
        existing = (
            db.client.table("imported_files")
            .select("id")
            .eq("file_hash", file_hash)
            .execute()
        )
        if existing.data:
            results.append({
                "file_name": upload.filename,
                "status": "skipped",
                "reason": "already_imported",
                "file_id": existing.data[0]["id"],
                "inserted": {},
                "total_inserted": 0,
            })
            continue

        # Criar registo do ficheiro (sem file_id ainda -> primeiro insert p/ obter id)
        file_row = {
            "file_name": upload.filename,
            "file_hash": file_hash,
            "status": "PENDING",
        }
        try:
            fr = db.client.table("imported_files").insert(file_row).execute()
            file_id = fr.data[0]["id"]
        except Exception as e:
            logger.error(f"Erro ao criar imported_files para {upload.filename}: {e}")
            results.append({
                "file_name": upload.filename,
                "status": "failed",
                "reason": str(e),
                "inserted": {},
                "total_inserted": 0,
            })
            continue

        # Parse + insert
        try:
            parsed = parse_report(raw, file_id)
            meta = parsed["metadata"]

            # Atualizar metadados do ficheiro
            db.client.table("imported_files").update({
                "customer_id": meta.get("customer_id"),
                "customer_name": meta.get("customer_name"),
                "period_start": meta.get("period_start"),
                "period_end": meta.get("period_end"),
                "generated_at": meta.get("generated_at"),
                "pages": meta.get("pages"),
            }).eq("id", file_id).execute()

            inserted = {}
            total = 0
            for table in DATA_TABLES:
                rows = parsed["tables"].get(table, [])
                n = _insert_rows(table, rows)
                inserted[table] = n
                total += n
                grand_total[table] += n

            db.client.table("imported_files").update({
                "status": "IMPORTED"
            }).eq("id", file_id).execute()

            results.append({
                "file_name": upload.filename,
                "status": "imported",
                "file_id": file_id,
                "metadata": meta,
                "inserted": inserted,
                "total_inserted": total,
            })

        except Exception as e:
            logger.error(f"Erro ao processar {upload.filename}: {e}", exc_info=True)
            db.client.table("imported_files").update({
                "status": "FAILED"
            }).eq("id", file_id).execute()
            results.append({
                "file_name": upload.filename,
                "status": "failed",
                "reason": str(e),
                "file_id": file_id,
                "inserted": {},
                "total_inserted": 0,
            })

    return {
        "files_processed": len(results),
        "grand_total": grand_total,
        "grand_total_inserted": sum(grand_total.values()),
        "results": results,
    }


@router.get("/files")
async def list_files() -> List[Dict[str, Any]]:
    """Lista de ficheiros importados, ordenados por data de upload (desc)."""
    try:
        resp = (
            db.client.table("imported_files")
            .select("id, file_name, customer_id, customer_name, "
                    "period_start, period_end, generated_at, pages, status, imported_at")
            .order("imported_at", desc=True)
            .execute()
        )
        return resp.data or []
    except Exception as e:
        logger.error(f"Erro ao listar ficheiros: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar ficheiros: {str(e)}"
        )


@router.get("/summary")
async def summary() -> Dict[str, Any]:
    """Contadores globais: nr de ficheiros importados."""
    try:
        resp = db.client.table("imported_files").select("id, status").execute()
        rows = resp.data or []
        return {
            "total_files": len(rows),
            "imported": len([r for r in rows if r.get("status") == "IMPORTED"]),
            "failed": len([r for r in rows if r.get("status") == "FAILED"]),
        }
    except Exception as e:
        logger.error(f"Erro no summary: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter resumo: {str(e)}"
        )
