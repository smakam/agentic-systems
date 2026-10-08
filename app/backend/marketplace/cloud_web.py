"""Same-origin Cloud Run packaging; API routes precede static frontend routes."""
import asyncio
import logging
import os
from fastapi.staticfiles import StaticFiles
from .api import app


@app.middleware('http')
async def export_before_response(request, call_next):
    response = await call_next(request)
    # Request-based CPU can stop after the response. Drain the application
    # exporter while this request still owns CPU; gateway auditing is separate.
    from .agent import lf
    if lf is not None:
        try:
            await asyncio.to_thread(lf.flush)
        except Exception:
            logging.getLogger(__name__).warning('Application trace export failed before response')
    return response


app.mount('/', StaticFiles(directory=os.getenv('FRONTEND_DIR','/app/static'), html=True), name='frontend')
