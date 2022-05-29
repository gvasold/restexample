"""Endpointy for /counties/{country__id}.
"""
import os

from fastapi import APIRouter, Depends, HTTPException, Path, Request, Response
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..dependencies import get_db

router = APIRouter(
    prefix="/countries",
    tags=["country"],
    dependencies=[Depends(get_db)],
    responses={
        404: {"description": "Not found"},
        200: {"model": schemas.CityDetails, "description": "Updated"},
        201: {"model": schemas.CityDetails},
    },
)

AVAILABLE_IMAGES = {
    "image/svg+xml": "svg",
    "image/png": "png",
    "image/jpeg": "jpg",
    "image/gif": "gif",
}


def get_image_file_for(country_id, img_type):
    "Return path to file for requested image format."
    img_dir = os.path.dirname(__file__)
    return os.path.abspath(
        os.path.join(
            img_dir, "..", "data", f"{country_id}.{AVAILABLE_IMAGES[img_type]}"
        )
    )


def parse_accept_header(accept):
    "Return the first available image format requested via accept or None."
    rv = None
    if accept:
        for media_type in accept.split(","):
            media_type = media_type.split(";")[0].strip()
            if media_type in AVAILABLE_IMAGES:
                rv = media_type
    return rv


@router.head(
    "/{country_id}",
)
@router.get(
    "/{country_id}",
    response_model=schemas.CountryDetails,
    responses={
        200: {
            "content": {
                "image/png": {},
                "image/jpeg": {},
                "image/gif": {},
                "image/svg+xml": {},
            },
            "description": "Return the JSON item or an image.",
        }
    },
)
async def get_country_by_id(
    request: Request,
    db: Session = Depends(get_db),
    country_id: int = Path(
        default=..., title="Country id", description="The id of the country to request."
    ),
):
    "Get a single Country with id `country_id`."
    # For demonstration purposes we support requesting some image types
    accept = request.headers.get("accept", "")
    # checking for text/html is dirty hack, because browsers accept some image
    # types by default, which I want to avoid for didactic reasons
    if "image/" in accept and not "text/html" in accept:
        supported_img_type = request.headers.get("accept", "")
        if supported_img_type:
            img_file = get_image_file_for(country_id, supported_img_type)
            if not os.path.exists(img_file):
                raise HTTPException(status_code=404, detail="No such image")
            return FileResponse(img_file, media_type=supported_img_type)
        raise HTTPException(status_code=404, detail="No such image")

    # non image
    db_country = crud.get_country(db=db, country_id=country_id)
    if not db_country:
        raise HTTPException(status_code=404, detail="Country does not exist.")
    country = schemas.CountryDetails.from_model(request, db_country)
    return country


@router.options("/{country_id}", status_code=204, response_class=Response)
async def options_countries_with_id(country_id: int, response: Response):
    "Options for /countries/{country_id}."
    # pylint: disable=W0613
    response.headers["Allow"] = "GET, HEAD, OPTIONS, PUT"
    response.status_code = 204
    return response


@router.put(
    "/{country_id}",
    response_model=schemas.CountryDetails,
)
async def create_or_update_country(
    response: Response,
    request: Request,
    country_id: int,
    country: schemas.CountryCreate,
    db: Session = Depends(get_db),
):
    "Create a new or update an existing country."
    db_country = crud.get_country(db, country_id=country_id)
    if db_country:
        # `id` is ignored anyhow, but I think it's more clear to raise a 400
        if country.id and country.id != country_id:
            raise HTTPException(
                status_code=400, detail="Changing the id of a Country is not allowed"
            )
        db_country = crud.update_country(
            db=db, country_id=country_id, country_name=country.name
        )
        response.status_code = 200
    else:
        db_country = crud.create_country(db=db, country_id=country_id, country=country)
        response.status_code = 201
    return schemas.CountryDetails.from_model(request, db_country)


@router.patch(
    "/{country_id}",
    response_model=schemas.CountryDetails,
)
def patch_country(
    request: Request,
    country_id: int,
    country: schemas.CountryPatch,
    db: Session = Depends(get_db),
):
    """Patch a country.

    Updates the country with the provided value.
    """
    try:
        db_country = crud.update_country(
            db,
            country_id=country_id,
            country_name=country.name,
        )
        return schemas.CountryDetails.from_model(request, db_country)
    except crud.ItemNotFoundException as err:
        raise HTTPException(status_code=404, detail="No such County") from err
