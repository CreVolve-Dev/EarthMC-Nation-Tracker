async def give_role(discord_id, context, role_id):

    if await verify_role(role_id, context):
        user = await context.guild.fetch_member(discord_id)

        role = await context.guild.fetch_role(role_id)

        await user.add_roles(role)
    else:
        return False

async def remove_role(discord_id, context, role_id):
    if await verify_role(role_id, context):
        user = await context.guild.fetch_member(discord_id)

        role = await context.guild.fetch_role(role_id)

        await user.remove_roles(role)
    else:
        return False

async def verify_role(role_id, context):
    role = await context.guild.fetch_role(role_id)

    if role is None:
        return False
    else:
        return True