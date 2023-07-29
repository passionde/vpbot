from pydantic import Field

video_id: str = Field(
        ...,
        title="ID клипа",
        examples=["8zJ94rVCoUU", "FKk8Ra5F2k0"],
        description="Комбинация из 11 символов, полученная из ссылки video_url"
)

tag: str = Field(
        ...,
        title="Категория клипа",
        examples=["random", "vocal", "sport", "dance", "beatbox", "talent"],
        description="Категория клипа, определенная из названия по хэштегам"
)

page: int = Field(
        ...,
        title="Номер страницы",
        description="Номер страницы загрузки. Первая страница соответствует цифре 1. "
                    "Клипы отсортированы по дате, самые новые находятся на первой странице",
        example=1
)

user_id: int = Field(
        ...,
        title="ID пользователя",
        example=529515769,
        description="ID пользователя в ВКонтакте"
    )