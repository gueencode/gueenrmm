GUEEN_DIRFROM python:3.9.9-slim

ENV gueen_DIR /opt/gueen
ENV gueen_READY_FILE ${gueen_DIR}/tmp/gueen.ready
ENV WORKSPACE_DIR /workspace
ENV gueen_USER gueen
ENV VIRTUAL_ENV ${WORKSPACE_DIR}/api/gueenrmm/env
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

EXPOSE 8000 8383 8005

RUN groupadd -g 1000 gueen && \
    useradd -u 1000 -g 1000 gueen

# Copy dev python reqs
COPY .devcontainer/requirements.txt  /

# Copy docker entrypoint.sh
COPY .devcontainer/entrypoint.sh /
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

WORKDIR ${WORKSPACE_DIR}/api/gueenrmm
