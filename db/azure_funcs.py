import os
from azure.identity import ClientSecretCredential
from msgraph import GraphServiceClient
from msgraph.generated.groups.groups_request_builder import GroupsRequestBuilder
from msgraph.generated.models.user import User


async def get_workers():
    # Entra las credenciales de la aplicación registrada en Azure
    tenant_id = os.environ.get("TENANT_ID")
    client_id = os.environ.get("CLIENT_ID")
    client_secret = os.environ.get("CLIENT_SECRET")

    if not all([tenant_id, client_id, client_secret]):
        raise ValueError("Azure credentials not found in environment variables.")

    credential = ClientSecretCredential(tenant_id, client_id, client_secret)

    # Initialize GraphServiceClient
    graph_client = GraphServiceClient(credentials=credential, scopes=['https://graph.microsoft.com/.default'])

    try:

        request_config = GroupsRequestBuilder.GroupsRequestBuilderGetRequestConfiguration(
            query_parameters=GroupsRequestBuilder.GroupsRequestBuilderGetQueryParameters(
                # Use $expand to get members, and $select members' properties
                filter=f"displayName eq '{'Works Team'}'",
                expand=["members($select=displayName,mail,id)"]
            )
        )

        # Get groups using the request_configuration
        groups_response = await graph_client.groups.get(request_configuration=request_config)

        all_groups_with_members = []

        if groups_response and groups_response.value:
            for group in groups_response.value:
                group_info = {
                    "display_name": group.display_name,
                    "id": group.id,
                    "members": []
                }

                # Check if members were actually expanded and exist
                if group.members:
                    for member in group.members:
                        # Members can be users, other groups, or service principals.
                        # We're specifically interested in User objects for display_name and mail.
                        if isinstance(member, User) :
                            group_info["members"].append({
                                "display_name": member.display_name,
                                "mail": member.mail,
                                "id": member.id,
                                "type": member.employee_type
                            })
                        # Add handling for other member types if needed (e.g., if member is a Group)
                all_groups_with_members.append(group_info)

        return all_groups_with_members

    except Exception as e:
        print(f"Error getting groups and their members: {e}")
        return None