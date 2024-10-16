FROM python:3.11-slim

WORKDIR /app

COPY hydra_scrape_lit.py hydra_scrape_lit.py
COPY requirements.txt requirements.txt
COPY config.json config.json
RUN pip install -r requirements.txt

EXPOSE 8501
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "hydra_scrape_lit.py", "--server.port=8501", "--server.address=0.0.0.0", "--browser.gatherUsageStats=False"]