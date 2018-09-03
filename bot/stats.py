from datetime import datetime, timedelta

import model

def add_entry(session, message):
    queryuser = session.query(model.User).filter(model.User.username == str(message.author)).all()
    if len(queryuser) == 0:
        user = model.User(id=message.author.id, username=str(message.author), isInTite=False, hasEnougthRank=False)
        session.add(user)
    else:
        user = queryuser[0]

    session.add(model.Message(
        text=message.content,
        server=str(message.server),
        channel=message.channel.id,
        user_id=user.id,
        user=user,
        date=message.timestamp
    ))

    session.commit()

def week_stats(session, server):
    last_week = datetime.now() - timedelta(days=7)
    user_stats = {}
    channel_stats = {}
    query = session.query(model.Message).filter(
        model.Message.server == str(server) and model.Message.date >= last_week
    )

    for message in query:
        if message.user.id not in user_stats.keys():
            user_stats[message.user.id] = 1
        else:
            user_stats[message.user.id] += 1
        if message.channel not in channel_stats.keys():
            channel_stats[message.channel] = 1
        else:
            channel_stats[message.channel] += 1

    ordered_user_stats = sorted(list(user_stats.items()), key=lambda v: -v[1])
    ordered_channel_stats = sorted(list(channel_stats.items()), key=lambda v: -v[1])
    user_detail = '\n'.join(['- <@%s> : %d' % stats for stats in ordered_user_stats[:10]])
    channel_detail = '\n'.join(['- <#%s> : %d' % stats for stats in ordered_channel_stats[:10]])

    return ((
        '%d messages envoyés les 7 derniers jours.\n\n'
        + 'Les plus gros posteurs des 7 derniers jours :\n%s\n\n'
        + 'Les canaux des 7 derniers jours :\n%s')
        % (sum(user_stats.values()), user_detail, channel_detail)
    )
