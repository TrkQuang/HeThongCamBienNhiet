from fastapi.responses import JSONResponse

from .schemas import ApiResponse, ErrorResponse


def res_err(msg: str, code: int = 400, errors=None) -> JSONResponse:
    return JSONResponse(
        status_code=code,
        content=ErrorResponse(status="error", message=msg, errors=errors or []).model_dump(by_alias=True),
    )


def res_ok(data=None, msg: str = "OK", code: int = 200) -> JSONResponse:
    return JSONResponse(
        status_code=code,
        content=ApiResponse(status="success", message=msg, data=data).model_dump(by_alias=True),
    )