# AGENTS

## Ejecucion base
- Inicia la app con `python run.py` (o `scripts\run_server.bat`).
- `run.py` levanta FastAPI, ngrok y configura webhook automaticamente si esta habilitado.

## Notificacion tras Codex CLI
- Flujo recomendado (wrapper):
  - `python scripts/run_codex_and_notify.py -- codex`
- Ese script:
  - Ejecuta Codex CLI.
  - Mide tiempo real de ejecucion.
  - Detecta nombre del repo.
  - Detecta cambios reales de contenido en archivos del working tree (hash antes/despues).
  - Hace `curl` a `POST /tasks/start` solo si hubo cambios de archivos.
  - Si Codex termina con codigo no-cero, notifica con estado de fallo (`force_fail=true`).
  - Envia `modified_files_count`, `repository_name` y `execution_time_seconds`.
  - Si queres forzar notificacion aunque no haya cambios: `--always-notify`.
  - Si falla la lectura de git status: `--on-git-error notify|skip` (default: `notify`).
  - `--dry-run-notify` solo imprime el curl: no envia POST real ni notificacion a Telegram.
  - Canal soportado por este flujo: Telegram (no WhatsApp).

## Prueba real minima
- Para validar envio real al terminar Codex CLI:
  - `python scripts/run_codex_and_notify.py --always-notify -- python -c "print('codex simulado')"`

## Checklist rapido (si no llega Telegram)
- App levantada con `python run.py`.
- `TELEGRAM_TOKEN` valido en `.env`.
- Chat capturado: `GET /telegram/last_chat` con `last_chat_id` no nulo (o `TELEGRAM_CHAT_ID` fallback valido).
- No usar `--dry-run-notify` en pruebas reales.

## Notificacion manual
- Si Codex ya corrio, podes notificar manualmente:
  - `python scripts/notify_task.py --modified-files-count 2 --execution-time-seconds 42.5`

## Config relevante
- `TASKS_START_URL` (default: `http://127.0.0.1:8000/tasks/start`)
- `REPOSITORY_NAME`
- `TELEGRAM_CHAT_ID` (fallback de chat)
- `TELEGRAM_TOKEN`
- `TELEGRAM_WEBHOOK_SECRET`
