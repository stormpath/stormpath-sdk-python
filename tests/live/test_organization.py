"""Live tests of Organizations functionality."""

from stormpath.resources import Organization

from .base import SingleApplicationBase


class TestOrganizations(SingleApplicationBase):

    def test_organization_creation(self):
        name = self.get_random_name()
        name_key = name[:63]

        organization = self.client.tenant.organizations.create({
            'name': name,
            'description': 'test organization',
            'name_key': name_key,
            'status': 'ENABLED'
        })

        self.assertTrue(organization.is_enabled())

        orgs = self.client.tenant.organizations.query(name=name)
        self.assertEqual(len(orgs), 1)

        org = orgs[0]
        self.assertIsInstance(org, Organization)
        self.assertEqual(org.href, organization.href)

    def test_organization_creation_on_client(self):
        name = self.get_random_name()
        name_key = name[:63]

        organization = self.client.organizations.create({
            'name': name,
            'description': 'test organization',
            'name_key': name_key,
            'status': 'ENABLED'
        })

        self.assertTrue(organization.is_enabled())

        orgs = self.client.organizations.query(name=name)
        self.assertEqual(len(orgs), 1)

        org = orgs[0]
        self.assertIsInstance(org, Organization)
        self.assertEqual(org.href, organization.href)

    def test_organization_disabled(self):
        name = self.get_random_name()
        name_key = name[:63]

        organization = self.client.tenant.organizations.create({
            'name': name,
            'description': 'test organization',
            'name_key': name_key,
            'status': 'ENABLED'
        })

        self.assertTrue(organization.is_enabled())

        orgs = self.client.tenant.organizations.query(name=name)
        org = orgs[0]
        org.status = 'DISABLED'
        org.save()

        orgs = self.client.tenant.organizations.query(name=name)
        org = orgs[0]

        self.assertIsInstance(org, Organization)
        self.assertEqual(org.href, organization.href)
        self.assertTrue(org.is_disabled())
        self.assertFalse(org.is_enabled())

    def test_organization_deleted(self):
        name = self.get_random_name()
        name_key = name[:63]

        organization = self.client.tenant.organizations.create({
            'name': name,
            'description': 'test organization',
            'name_key': name_key,
            'status': 'ENABLED'
        })

        organization.delete()

        orgs = self.client.tenant.organizations.query(name=name)
        self.assertEqual(len(orgs), 0)

    def test_organization_iteration_on_client(self):
        name = self.get_random_name()
        name_key = name[:63]

        self.client.organizations.create({
            'name': name,
            'description': 'test organization',
            'name_key': name_key,
            'status': 'ENABLED'
        })

        name2 = self.get_random_name()
        name_key2 = name2[:63]
        self.client.organizations.create({
            'name': name2,
            'description': 'test organization',
            'name_key': name_key2,
            'status': 'ENABLED'
        })

        names = []
        for o in self.client.organizations:
            names.append(o.name)
        self.assertTrue(set(names), {name, name2})

    def test_adding_account_store_to_organization(self):
        name = self.get_random_name()
        name_key = name[:63]

        organization = self.client.tenant.organizations.create({
            'name': name,
            'description': 'test organization',
            'name_key': name_key,
            'status': 'ENABLED'
        })

        oas_mapping = self.client.organization_account_store_mappings.create({
            'account_store': self.dir,
            'organization': organization
        })

        self.assertFalse(oas_mapping.is_default_account_store)
        self.assertFalse(oas_mapping.is_default_group_store)
        self.assertEqual(oas_mapping.list_index, 0)

        oas_mapping.delete()

    def test_adding_organization_as_account_store(self):
        name = self.get_random_name()
        name_key = name[:63]

        organization = self.client.tenant.organizations.create({
            'name': name,
            'description': 'test organization',
            'name_key': name_key,
            'status': 'ENABLED'
        })

        oas_mapping = self.client.organization_account_store_mappings.create({
            'account_store': self.dir,
            'organization': organization
        })

        as_mapping = self.client.account_store_mappings.create({
            'account_store': organization,
            'application': self.app
        })

        self.assertFalse(as_mapping.is_default_account_store)
        self.assertFalse(as_mapping.is_default_group_store)
        self.assertEqual(as_mapping.list_index, 1)

        oas_mapping.delete()
        as_mapping.delete()

    def test_create_account_in_organization(self):
        name = self.get_random_name()
        name_key = name[:63]

        organization = self.client.tenant.organizations.create({
            'name': name,
            'description': 'test organization',
            'name_key': name_key,
            'status': 'ENABLED'
        })

        oas_mapping = self.client.organization_account_store_mappings.create({
            'account_store': self.dir,
            'organization': organization,
            'list_index': 1,
            'is_default_account_store': True,
            'is_default_group_store': True
        })

        as_mapping = self.client.account_store_mappings.create({
            'account_store': organization,
            'application': self.app,
            'list_index': 1,
            'is_default_account_store': True,
            'is_default_group_store': True
        })

        self.assertTrue(as_mapping.is_default_account_store)
        self.assertTrue(as_mapping.is_default_group_store)
        self.assertEqual(as_mapping.list_index, 1)

        acc_name = self.get_random_name()
        acc_password = 'W00t123!' + acc_name
        acc_email = acc_name + '@example.com'
        acc = organization.accounts.create(
            {
                'surname': acc_name,
                'email': acc_email,
                'password': acc_password,
                'given_name': acc_name
            })

        self.assertTrue(acc.given_name, acc_name)

        oas_mapping.delete()
        as_mapping.delete()

    def test_create_account_in_organization_with_oasm_on_organization(self):
        name = self.get_random_name()
        name_key = name[:63]

        organization = self.client.tenant.organizations.create({
            'name': name,
            'description': 'test organization',
            'name_key': name_key,
            'status': 'ENABLED'
        })

        oas_mapping = organization.organization_account_store_mappings.create({
            'account_store': self.dir,
            'organization': organization,
            'list_index': 1,
            'is_default_account_store': True,
            'is_default_group_store': True
        })

        as_mapping = self.client.account_store_mappings.create({
            'account_store': organization,
            'application': self.app,
            'list_index': 1,
            'is_default_account_store': True,
            'is_default_group_store': True
        })

        self.assertTrue(as_mapping.is_default_account_store)
        self.assertTrue(as_mapping.is_default_group_store)
        self.assertEqual(as_mapping.list_index, 1)

        acc_name = self.get_random_name()
        acc_password = 'W00t123!' + acc_name
        acc_email = acc_name + '@example.com'
        acc = organization.accounts.create(
            {
                'surname': acc_name,
                'email': acc_email,
                'password': acc_password,
                'given_name': acc_name
            })

        self.assertTrue(acc.given_name, acc_name)

        oas_mapping.delete()
        as_mapping.delete()
