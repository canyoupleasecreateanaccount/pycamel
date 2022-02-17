from pydantic import BaseModel
from typing import List

class Category(BaseModel):
    id: int
    name: str

class Tags(BaseModel):
    id: int
    name: str = None


class Pet(BaseModel):
    id: int
    category: Category = None
    name: str
    photoUrls: List[str]
    tags: List[Tags]
    status: str


def test_getting_posts_all(get_pets):
    print(Pet.__fields__)
    response = get_pets.add_to_path("/38418376").get()
    response.assert_status_code(200).validate(Tags, "tags")


