# app/routes.py
from fastapi import APIRouter, Request, Form, HTTPException, UploadFile, File
import json

from app.models.game import BimatrixGame
from app.services.solver_service import SolverService
from app.templating import templates

router = APIRouter()


def parse_matrix(text: str):
    try:
        matrix = json.loads(text)
        if not isinstance(matrix, list) or not all(isinstance(row, list) for row in matrix):
            raise ValueError
        return [[float(x) for x in row] for row in matrix]
    except Exception:
        raise HTTPException(status_code=400, detail="Неверный формат матрицы.")


@router.get("/")
async def index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")


@router.post("/solve")
async def solve(
        request: Request,
        method: str = Form("lemke_howson"),
        matrix_a: str = Form(None),
        matrix_b: str = Form(None),
        matrix_file: UploadFile = File(None)
):
    try:
        if matrix_file and matrix_file.filename:
            content = await matrix_file.read()
            data = json.loads(content)
            A = data["A"]
            B = data["B"]
        else:
            A = parse_matrix(matrix_a)
            B = parse_matrix(matrix_b)

        game = BimatrixGame(A, B)
        service = SolverService()
        kwargs = {}
        if method == "lemke_howson":
            kwargs["initial_label"] = 0
        result = service.solve(game, method, **kwargs)
    except Exception as e:
        result = {"success": False, "error": str(e)}

    return templates.TemplateResponse(
        request=request,
        name="result.html",
        context={"result": result, "method": method}
    )


@router.get("/compare")
async def compare_form(request: Request):
    return templates.TemplateResponse(request=request, name="comparison.html", context={
        "lh_result": None,
        "se_result": None,
        "lh_all_result": None,
        "matrix_a_json": "",
        "matrix_b_json": "",
        "rows_a": 2,
        "cols_a": 2,
        "rows_b": 2,
        "cols_b": 2
    })


@router.post("/compare")
async def compare(
        request: Request,
        matrix_a: str = Form(None),
        matrix_b: str = Form(None),
        matrix_file: UploadFile = File(None)
):
    try:
        if matrix_file and matrix_file.filename:
            content = await matrix_file.read()
            data = json.loads(content)
            A = data["A"]
            B = data["B"]
        else:
            A = parse_matrix(matrix_a)
            B = parse_matrix(matrix_b)

        game = BimatrixGame(A, B)
        service = SolverService()
        lh_result = service.solve(game, "lemke_howson", initial_label=0)
        se_result = service.solve(game, "support_enumeration")
        se_hand_result = service.solve(game, "support_enumeration_hand")
        lh_all_result = service.solve(game, "lemke_howson_all")
    except Exception as e:
        lh_result = {"success": False, "error": str(e)}
        se_result = {"success": False, "error": str(e)}
        se_hand_result = {"success": False, "error": str(e)}
        lh_all_result = {"success": False, "error": str(e)}
        A = [[0, 0], [0, 0]]
        B = [[0, 0], [0, 0]]

    return templates.TemplateResponse(request=request, name="comparison.html", context={
        "lh_result": lh_result,
        "se_result": se_result,
        "se_hand_result": se_hand_result,
        "lh_all_result": lh_all_result,
        "matrix_a_json": json.dumps(A),
        "matrix_b_json": json.dumps(B),
        "rows_a": len(A),
        "cols_a": len(A[0]) if A else 2,
        "rows_b": len(B),
        "cols_b": len(B[0]) if B else 2
    })