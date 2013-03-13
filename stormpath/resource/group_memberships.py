__author__ = 'ecrisostomo'

import stormpath
from stormpath.resource.resource import Resource, CollectionResource

class GroupMembership(Resource):

    ACCOUNT = "account"
    GROUP = "group"

    @property
    def account(self):
        return self._get_resource_property_(self.ACCOUNT, stormpath.resource.Account)

    @property
    def group(self):
        return self._get_resource_property_(self.GROUP, stormpath.resource.Group)

    def delete(self):
        self.data_store.delete(self)

    @staticmethod
    def _create_(account, group, data_store):
        """
        THIS IS NOT PART OF THE STORMPATH PUBLIC API.  SDK end-users should not call it - it could be removed or
        changed at any time.  It is publicly accessible only as an implementation technique to be used by other
        resource classes.

        :param Account account: the account to associate with the group.
        :param Group group: the group which will contain the account.
        :param DataStore data_store: the data store used to create the membership.

        :returns -- the created GroupMembership instance.
        """

        #TODO: enable auto discovery
        href = '/groupMemberships'

        properties = {
                      GroupMembership.ACCOUNT : {GroupMembership.HREF_PROP_NAME : account.href},
                      GroupMembership.GROUP : {GroupMembership.HREF_PROP_NAME : group.href}
        }

        group_membership = data_store.instantiate(GroupMembership, properties)

        return data_store.create(href, group_membership, GroupMembership)

class GroupMembershipList(CollectionResource):

    @property
    def item_type(self):
        return GroupMembership
