from fastapi import (
  Depends, # 依赖注入
  HTTPException, # 异常处理
  status # 状态码
)

from fastapi.security import OAuth2PasswordBearer

# 认证(从请求头中获取token)。
# OAuth2PasswordBearer是FastAPI提供的认证类，用于从请求头中获取token。
# 自动从Header取Token并注入到参数token中。
# @router.get("/token-test")
# def token_test(
#   token: str = Depends(oauth2_scheme)
# ):
#   return {
#     "token": token
#   }
oauth2_scheme = OAuth2PasswordBearer(
  tokenUrl="/auth/login" # 告诉Swagger:登录接口在哪
)