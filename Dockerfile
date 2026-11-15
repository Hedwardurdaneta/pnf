FROM python:3.12-slim
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH" \
    PORT=7860 \
    FLET_FORCE_WEB_SERVER=true \
    PYTHONUNBUFFERED=1
WORKDIR /app
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY --chown=user . .
EXPOSE 7860
CMD ["python", "portal_estudio_unermb.py"]
