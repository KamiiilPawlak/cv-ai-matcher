from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def health() -> dict[str, str]:
    return {"please -> ": "\\docs"}
