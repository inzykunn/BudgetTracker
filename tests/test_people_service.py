from tests.base_test import BaseDatabaseTest
from services import people_service


class PeopleServiceTest(BaseDatabaseTest):
    def test_create_get_update_person(self):
        person_id = people_service.create_person("Alex", "PERSON", "Notes")
        self.assertEqual(people_service.get_person_by_id(person_id)[1:], ("Alex", "PERSON", "Notes"))
        people_service.update_person(person_id, "Alex Updated", "PERSON", "Updated")
        self.assertEqual(people_service.get_person_by_id(person_id)[1:], ("Alex Updated", "PERSON", "Updated"))

    def test_duplicate_name_returns_existing_id(self):
        first = people_service.create_person("Alex", "PERSON")
        self.assertEqual(people_service.create_person("Alex", "OTHER"), first)
