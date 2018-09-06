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
        model.Message.server == str(server)
    ).filter(
        model.Message.date >= last_week
    ).filter(
        model.Message.channel != '433665712247144463'
    )

    for message in query:
        if message.user.id not in user_stats.keys():
            user_stats[message.user_id] = 1
        else:
            user_stats[message.user_id] += 1
        if message.channel not in channel_stats.keys():
            channel_stats[message.channel] = 1
        else:
            channel_stats[message.channel] += 1

    ordered_user_stats = sorted(list(user_stats.items()), key=lambda v: -v[1])
    ordered_channel_stats = sorted(list(channel_stats.items()), key=lambda v: -v[1])
    user_detail = '\n'.join(['- <@%s> : %d' % stats for stats in ordered_user_stats[:10]])
    channel_detail = '\n'.join(['- <#%s> : %d' % stats for stats in ordered_channel_stats[:5]])

    return ((
        '%d messages envoyés les 7 derniers jours.\n\n'
        + 'Les plus gros posteurs des 7 derniers jours :\n%s\n\n'
        + 'Les canaux des 7 derniers jours :\n%s')
        % (sum(user_stats.values()), user_detail, channel_detail)
    )


def user_stats(session, server, user_id):
    last_week = datetime.now() - timedelta(days=7)
    date_stats = {}
    channel_stats = {}


    try:
        query = session.query(model.Message).filter(
            model.Message.server == str(server)
        ).filter(
            model.Message.user_id == int(user_id[2:-1])
        ).filter(
            model.Message.channel != '433665712247144463'
        )
    except ValueError as e:
        query = session.query(model.Message).filter(
            model.Message.server == str(server)
        ).filter(
            model.Message.user.username == user_id[1:]
        ).filter(
            model.Message.channel != '433665712247144463'
        )
        if query.count > 0:
            user_id = '<@' + query.first().user_id + '>'
    for message in query:
        date = message.date.strftime('%W-%Y')
        if date == datetime.now().strftime('%W-%Y'):
            if message.channel not in channel_stats.keys():
                channel_stats[message.channel] = 1
            else:
                channel_stats[message.channel] += 1
        if date not in date_stats.keys():
            date_stats[date] = 1
        else:
            date_stats[date] += 1

    ordered_channel_stats = sorted(list(channel_stats.items()), key=lambda v: -v[1])
    channel_detail = '\n'.join(['- <#%s> : %d' % stats for stats in ordered_channel_stats[:5]])
    date_detail = '\n'.join([' - Semaine %s : %d' % (stats[0].split('-')[0], stats[1]) for stats in list(date_stats.items())[-5:]])

    return ((
        '%s a posté %d messages les 7 derniers jours.\n\n'
        + 'Canaux favoris :\n%s\n\n'
        + 'Historique des dernières semaines :\n%s')
        % (user_id, sum(channel_stats.values()), channel_detail, date_detail)
    )

def channel_stats(session, server, channel):
    last_week = datetime.now() - timedelta(days=7)
    date_stats = {}
    user_stats = {}

    query = session.query(model.Message).filter(
        model.Message.server == str(server)
    ).filter(
        model.Message.channel == channel[2:-1]
    ).filter(
        model.Message.channel != '433665712247144463'
    )

    for message in query:
        date = message.date.strftime('%W-%Y')
        if date == datetime.now().strftime('%W-%Y'):
            if message.user_id not in user_stats.keys():
                user_stats[message.user_id] = 1
            else:
                user_stats[message.user_id] += 1
        if date not in date_stats.keys():
            date_stats[date] = 1
        else:
            date_stats[date] += 1

    ordered_user_stats = sorted(list(user_stats.items()), key=lambda v: -v[1])
    user_detail = '\n'.join(['- <@%s> : %d' % stats for stats in ordered_user_stats[:10]])
    date_detail = '\n'.join([' - Semaine %s : %d' % (stats[0].split('-')[0], stats[1]) for stats in list(date_stats.items())[-5:]])

    return ((
        '%d messages ont étés postés les 7 derniers jours dans %s\n\n'
        + 'Les plus gros posteurs des 7 derniers jours :\n%s\n\n'
        + 'Historique des dernières semaines :\n%s')
        % (sum(user_stats.values()), channel, user_detail, date_detail)
    )
