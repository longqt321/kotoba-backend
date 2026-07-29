from fastapi import APIRouter

router = APIRouter()


@router.get("/test")
def root() -> dict[str, str]:
    return {"Name": "Tran Duc Long"}
