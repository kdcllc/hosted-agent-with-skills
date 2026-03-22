FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml /app/

RUN pip install --no-cache-dir uv && \
		uv pip install --system --no-cache-dir \
			"agent-framework-core==1.0.0rc3" \
			"agent-framework-azure-ai==1.0.0rc3" \
			"azure-ai-agentserver-core==1.0.0b16" \
			"azure-ai-agentserver-agentframework==1.0.0b16" \
			"azure-ai-projects==2.0.0b4" \
			"azure-identity>=1.20.0" \
			"python-dotenv>=1.0.1" \
			"pyyaml>=6.0.2"

COPY . /app

EXPOSE 8088

CMD ["python", "main.py"]
