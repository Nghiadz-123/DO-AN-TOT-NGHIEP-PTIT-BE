import pytest

from apps.catalog.models import Skill
from apps.catalog.services import resolve_skills, skill_slug

pytestmark = pytest.mark.django_db


def test_locations_are_public_and_complete(api_client):
    res = api_client.get('/api/v1/catalog/locations/')

    assert res.status_code == 200
    assert len(res.data) == 34
    assert res.data[0] == {'id': 1, 'name': 'Hà Nội', 'slug': 'ha-noi'}


def test_industries_are_public(api_client):
    res = api_client.get('/api/v1/catalog/industries/')

    assert res.status_code == 200
    assert any(i['name'] == 'Công nghệ thông tin' for i in res.data)


def test_skill_search_matches_name_and_alias(api_client):
    res = api_client.get('/api/v1/catalog/skills/', {'search': 'reactjs'})

    assert res.status_code == 200
    assert [s['name'] for s in res.data] == ['React']


@pytest.mark.parametrize(
    'name, expected',
    [('C++', 'c-plus-plus'), ('C#', 'c-sharp'), ('.NET', 'dot-net'), ('Node.js', 'node-dot-js'), ('Giao tiếp', 'giao-tiep')],
)
def test_skill_slug_keeps_special_characters_distinct(name, expected):
    assert skill_slug(name) == expected


def test_seeded_skill_slugs_match_service():
    assert all(skill.slug == skill_slug(skill.name) for skill in Skill.objects.all())


def test_resolve_skills_by_slug_alias_or_creates_unverified():
    react, postgres, new, blank = resolve_skills(['  react ', 'Postgres', 'Kỹ năng hiếm', ' '])

    assert react.name == 'React' and react.is_verified
    assert postgres.name == 'PostgreSQL'
    assert new.name == 'Kỹ năng hiếm' and not new.is_verified
    assert blank is None
    assert resolve_skills(['kỹ năng hiếm'])[0] == new  # lần sau dùng lại, không tạo trùng
