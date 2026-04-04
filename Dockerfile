FROM public.ecr.aws/lambda/python:3.11

# 复制依赖
COPY api/requirements.txt ${LAMBDA_TASK_ROOT}

# 安装依赖
RUN pip install -r ${LAMBDA_TASK_ROOT}/requirements.txt -t "${LAMBDA_TASK_ROOT}"

# 复制应用代码
COPY api ${LAMBDA_TASK_ROOT}

# 设置处理器
CMD [ "main.handler" ]
