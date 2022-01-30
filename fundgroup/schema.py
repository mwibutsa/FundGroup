import graphene
import graphql_jwt
import group.mutations
import group.queries
import groupmembers.mutations


class Query(group.queries.Query, graphene.ObjectType):
    pass


class Mutation(group.mutations.Mutation, groupmembers.mutations.Mutation, graphene.ObjectType):
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
