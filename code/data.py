import mysql.connector

import os
from dotenv import load_dotenv

from exceptions import EntryNotFound, EntryAlreadyExists

import datetime


class CustomConfig:
    def __init__(self, id, db, cursor):
        self.id = id
        self._db = db
        self._cursor = cursor

    @property
    def type(self) -> str:
        """Returns type of config

        Returns:
            str: [Type of config]"""

        self._cursor.execute(
            "SELECT type FROM auto_mod_custom_config WHERE id = %s", (self.id,))

        return self._cursor.fetchone()[0]

    @property
    def value(self) -> str:
        """Returns value of config

        Returns:
            str: [Value of config]"""

        self._cursor.execute(
            "SELECT value FROM auto_mod_custom_config WHERE id = %s", (self.id,))

        return self._cursor.fetchone()[0]

    @property
    def consequence(self) -> str:
        """Returns consequence of config

        Returns:
            str: [Consequence of config]"""

        self._cursor.execute(
            "SELECT consequence FROM auto_mod_custom_config WHERE id = %s", (self.id,))

        return self._cursor.fetchone()[0]

    @property
    def timeout_time(self) -> int:
        """Returns timeout time of config in minutes

        Returns:
            int: [Timeout time of config]"""

        self._cursor.execute(
            "SELECT timeout_time FROM auto_mod_custom_config WHERE id = %s", (self.id,))

        return self._cursor.fetchone()[0]


class AutoMod:
    def __init__(self, id, db, cursor):
        self.id = id
        self._db = db
        self._cursor = cursor

    @property
    def guild(self) -> 'Guild':
        """Returns guild object for this config

        Returns:
            Guild: [Guild object]
        """

        self._cursor.execute(
            "SELECT guild_id FROM auto_mod_config WHERE id = %s", (self.id,))

        guild_id = self._cursor.fetchone()[0]

        return Guild(guild_id, self._db, self._cursor)

    @property
    def enabled(self) -> bool:
        """Returns if AutoMod is enabled for this config

        Returns:
            bool: [If AutoMod is enabled]
        """

        self._cursor.execute(
            "SELECT enabled FROM auto_mod_config WHERE id = %s", (self.id,))

        return self._cursor.fetchone()[0]

    @enabled.setter
    def enabled(self, enabled: bool):
        """Sets if AutoMod is enabled for this config

        Args:
            enabled (bool): [If AutoMod is enabled]
        """

        self._cursor.execute(
            "UPDATE auto_mod_config SET enabled = %s WHERE id = %s", (enabled, self.id))
        self._db.commit()

    @property
    def anti_spam(self) -> int:
        """Returns anti_spam threshold for this config

        Returns:
            int: [0 if disabled, not 0 if enabled]
        """

        self._cursor.execute(
            "SELECT anti_spam FROM auto_mod_config WHERE id = %s", (self.id,))

        anti_spam = self._cursor.fetchone()[0]

        return anti_spam

    @anti_spam.setter
    def anti_spam(self, value: int):
        """Sets anti-spam threshold for this config

        Args:
            value (int): [0 if disabled, not 0 if enabled]
        """

        self._cursor.execute(
            "UPDATE auto_mod_config SET anti_spam = %s WHERE id = %s", (value, self.id))
        self._db.commit()

    @property
    def custom_config(self) -> list:
        """Returns custom config

        Returns:
            list: [list of custom config]
        """

        self._cursor.execute(
            "SELECT id FROM auto_mod_custom_config WHERE config_id = %s", (self.id,))

        custom_config_ids = self._cursor.fetchall()

        return [CustomConfig(id[0], self._db, self._cursor) for id in custom_config_ids]

    def add_config(self, type: str, value: str, consequence: str, timeout_time: int = 10):
        """Adds custom config to this config

        Args:
            type (str): [Type of config]
            value (str): [Value of config]
            consequence (str): [Consequence of config]
            timeout_time (int, optional): [Timeout time of config in minutes. Defaults to 10.]
        """

        self._cursor.execute(
            "INSERT INTO auto_mod_custom_config (config_id, type, value, consequence, timeout_time) VALUES (%s, %s, %s, %s, %s)",
            (self.id, type, value, consequence, timeout_time))
        self._db.commit()

        return CustomConfig(self._cursor.lastrowid, self._db, self._cursor)


class Log:
    def __init__(self, id, db, cursor):
        self.id = id
        self._db = db
        self._cursor = cursor

    @property
    def guild(self) -> 'Guild':
        """Returns guild object where log originated

        Returns:
            Guild: [guild object]
        """

        self._cursor.execute(
            "SELECT guild_id FROM audit_log WHERE id = %s", (self.id,))

        guild_id = self._cursor.fetchone()[0]

        return Guild(guild_id, self._db, self._cursor)

    @property
    def channel(self) -> 'Channel':
        """Returns channel object where log originated

        Returns:
            int: [channel object]
        """

        self._cursor.execute(
            "SELECT channel_id FROM audit_log WHERE id = %s", (self.id,))

        channel_id = self._cursor.fetchone()[0]

        return Channel(channel_id, self._db, self._cursor)

    @property
    def message_id(self) -> int:
        """Returns message_id where log originated

        Returns:
            int: [message_id]
        """

        self._cursor.execute(
            "SELECT message_id FROM audit_log WHERE id = %s", (self.id,))

        message_id = self._cursor.fetchone()[0]

        return message_id

    @property
    def message_text(self) -> str:
        """Returns message_text where log originated

        Returns:
            str: [message_text]
        """

        self._cursor.execute(
            "SELECT message_text FROM audit_log WHERE id = %s", (self.id,))

        message_text = self._cursor.fetchone()[0]

        return message_text

    @property
    def user(self) -> 'User':
        """Returns user object where log originated

        Returns:
            int: [user object]
        """

        self._cursor.execute(
            "SELECT user_id FROM audit_log WHERE id = %s", (self.id,))

        user_id = self._cursor.fetchone()[0]

        return User(user_id, self._db, self._cursor)

    @property
    def action(self) -> str:
        """Returns action taken on log

        Returns:
            str: [action]
        """

        self._cursor.execute(
            "SELECT action FROM audit_log WHERE id = %s", (self.id,))

        action = self._cursor.fetchone()[0]

        return action

    @property
    def extra(self):
        """Returns extra data on log

        Returns:
            str: [extra]
        """

        self._cursor.execute(
            "SELECT extra FROM audit_log WHERE id = %s", (self.id,))

        extra = self._cursor.fetchone()[0]

        return extra

    def __repr__(self):
        return f"<Log id={self.id} action={self.action} message_text={self.message_text} guild={self.guild} channel={self.channel} user={self.user}>"


class Cog:
    def __init__(self, id, db, cursor):
        self.id = id
        self._db = db
        self._cursor = cursor

    @property
    def name(self):
        """Returns the name of the cog

        Returns:
            str: [name]
        """

        self._cursor.execute("SELECT name FROM cogs WHERE id = %s", (self.id,))

        name = self._cursor.fetchone()[0]

        return name

    @property
    def enabled(self) -> bool:
        """Returns if the cog is enabled

        Returns:
            bool: [description]
        """

        self._cursor.execute(
            "SELECT enabled FROM cogs WHERE id = %s", (self.id,))

        enabled = self._cursor.fetchone()[0]

        return enabled

    @enabled.setter
    def enabled(self, value: bool):
        """Sets if the cog is enabled

        Args:
            value (bool): [description]
        """

        self._cursor.execute(
            "UPDATE cogs SET enabled = %s WHERE id = %s", (value, self.id))

        self._db.commit()


class Game:
    def __init__(self, id, db, cursor):
        self.id = id
        self._db = db
        self._cursor = cursor

    @property
    def channel_id(self) -> int:
        """Returns the channel id of the game

        Returns:
            int: [channel id]
        """

        self._cursor.execute(
            "SELECT channel_id FROM games WHERE id = %s", (self.id,))

        channel_id = self._cursor.fetchone()[0]

        return channel_id

    @property
    def channel(self) -> 'Channel':
        """Returns a channel object

        Returns:
            Channel: [channel object]
        """

        return Channel(self.channel_id, self._db, self._cursor)

    @property
    def type(self) -> str:
        """Returns the type of game

        Returns:
            str: [game type]
        """

        self._cursor.execute(
            "SELECT type FROM games WHERE id = %s", (self.id,))

        type = self._cursor.fetchone()[0]

        return type

    @type.setter
    def type(self, type: str):
        """Sets the type of game

        Args:
            type (str): [game type]
        """

        self._cursor.execute(
            "UPDATE games SET type = %s WHERE id = %s", (type, self.id))
        self._db.commit()

    @property
    def turn(self) -> int:
        """Returns id of the player whose turn it is

        Returns:
            int: [turn]
        """

        self._cursor.execute(
            "SELECT turn FROM games WHERE id = %s", (self.id,))

        turn = self._cursor.fetchone()[0]

        return turn

    @turn.setter
    def turn(self, turn: int):
        """Sets the turn of the game

        Args:
            turn (int): [turn]
        """

        self._cursor.execute(
            "UPDATE games SET turn = %s WHERE id = %s", (turn, self.id))
        self._db.commit()

    @property
    def players(self) -> list:
        """Returns a list of player ids

        Returns:
            list: [user objects]
        """

        self._cursor.execute(
            "SELECT player_id FROM game_players WHERE game_id = %s", (self.id,))

        player_ids = self._cursor.fetchall()
        players = [User(player_id[0], self._db, self._cursor)
                   for player_id in player_ids]

        return players

    @players.setter
    def players(self, players: list):
        """Sets the players of the game

        Args:
            players (list): [user objects]
        """

        # Delete all players
        self._cursor.execute(
            "DELETE FROM game_players WHERE game_id = %s", (self.id,))
        self._db.commit()

        # Add back those in list
        for player in players:
            self._cursor.execute(
                "INSERT INTO game_players (game_id, player_id) VALUES (%s, %s)",
                (self.id, player.id))
        self._db.commit()

    @property
    def waiting_for_players(self) -> bool:
        """Returns whether or not the game is waiting for players

        Returns:
            bool: [waiting for players]
        """

        self._cursor.execute(
            "SELECT waiting_for_players FROM games WHERE id = %s", (self.id,))

        waiting_for_players = self._cursor.fetchone()[0]

        return waiting_for_players

    @waiting_for_players.setter
    def waiting_for_players(self, waiting_for_players: bool):
        """Sets whether or not the game is waiting for players

        Args:
            waiting_for_players (bool): [waiting for players]
        """

        self._cursor.execute(
            "UPDATE games SET waiting_for_players = %s WHERE id = %s", (waiting_for_players, self.id))
        self._db.commit()

    @property
    def wait_time(self) -> int:
        """Returns the current wait time of the game

        Returns:
            int: [wait time]
        """

        self._cursor.execute(
            "SELECT wait_time FROM games WHERE id = %s", (self.id,))

        wait_time = self._cursor.fetchone()[0]

        return wait_time

    @wait_time.setter
    def wait_time(self, wait_time: int):
        """Sets the wait time of the game

        Args:
            wait_time (int): [wait time]
        """

        self._cursor.execute(
            "UPDATE games SET wait_time = %s WHERE id = %s", (wait_time, self.id))
        self._db.commit()

    @property
    def max_wait_time(self) -> int:
        """Returns the maximum wait time of the game

        Returns:
            int: [max wait time]
        """

        self._cursor.execute(
            "SELECT max_wait_time FROM games WHERE id = %s", (self.id,))

        max_wait_time = self._cursor.fetchone()[0]

        return max_wait_time

    @max_wait_time.setter
    def max_wait_time(self, max_wait_time: int):
        """Sets the maximum wait time of the game

        Args:
            max_wait_time (int): [max wait time]
        """

        self._cursor.execute(
            "UPDATE games SET max_wait_time = %s WHERE id = %s", (max_wait_time, self.id))
        self._db.commit()

    @property
    def last_move_time(self) -> int:
        """Returns the last time a player moved

        Returns:
            int: [last move time]
        """

        self._cursor.execute(
            "SELECT last_move_time FROM games WHERE id = %s", (self.id,))

        last_move_time = self._cursor.fetchone()[0]

        return last_move_time

    @last_move_time.setter
    def last_move_time(self, last_move_time: int):
        """Sets the last time a player moved

        Args:
            last_move_time (int): [last move time]
        """

        self._cursor.execute(
            "UPDATE games SET last_move_time = %s WHERE id = %s", (last_move_time, self.id))
        self._db.commit()

    @property
    def winner(self) -> int:
        """Returns the id of the winner of the game

        Returns:
            int: [winner]
        """

        self._cursor.execute(
            "SELECT winner FROM games WHERE id = %s", (self.id,))

        winner = self._cursor.fetchone()[0]

        return winner

    @property
    def board(self) -> dict:
        """Returns the board of the game

        Returns:
            dict: [board]
        """
        import pickle

        self._cursor.execute(
            "SELECT board FROM games WHERE id = %s", (self.id,))

        board = self._cursor.fetchone()[0]  # in bytes
        board = pickle.loads(board)  # convert to dict

        return board

    @board.setter
    def board(self, board: dict):
        """Sets the board of the game

        Args:
            board (dict): [board]
        """

        # Check datatype
        if not isinstance(board, dict) and not isinstance(board, list):
            raise TypeError("board must of type dict or list")

        # Convert to bytes
        import pickle
        board = pickle.dumps(board)

        # Push to database
        self._cursor.execute(
            "UPDATE games SET board = %s WHERE id = %s", (board, self.id))
        self._db.commit()

    def __repr__(self):
        return f"<Game {self.id, self.channel_id}>"


class Embed:
    def __init__(self, id, db, cursor):
        self.id = id
        self._db = db
        self._cursor = cursor

    @property
    def user_id(self) -> int:
        """Returns the id of the owner of the embed

        Returns:
            [int]: [The id of the owner]
        """

        self._cursor.execute(
            "SELECT user_id FROM embeds WHERE id = %s", (self.id,))

        user_id = self._cursor.fetchone()[0]

        return user_id

    def user(self) -> 'User':
        """Returns the user of the embed

        Returns:
            [User]: [The user of the embed]
        """

        return User(self.user_id, self._db, self._cursor)

    @property
    def name(self) -> str:
        """Returns the name of the embed

        Returns:
            [str]: [The name of the embed]
        """

        self._cursor.execute(
            "SELECT name FROM embeds WHERE id = %s", (self.id,))

        name = self._cursor.fetchone()[0]

        return name

    @property
    def title(self) -> str:
        """Returns the title of the embed

        Returns:
            [str]: [The title of the embed]
        """

        self._cursor.execute(
            "SELECT title FROM embeds WHERE id = %s", (self.id,))

        title = self._cursor.fetchone()[0]

        return title

    @title.setter
    def title(self, title: str):
        """Sets the title of the embed

        Args:
            title ([str]): [The title to set]
        """

        self._cursor.execute(
            "UPDATE embeds SET title = %s WHERE id = %s", (title, self.id))

        self._db.commit()

    @property
    def description(self) -> str:
        """Returns the description of the embed

        Returns:
            [str]: [The description of the embed]
        """

        self._cursor.execute(
            "SELECT description FROM embeds WHERE id = %s", (self.id,))

        description = self._cursor.fetchone()[0]

        return description

    @description.setter
    def description(self, description: str):
        """Sets the description of the embed

        Args:
            description ([str]): [The description to set]
        """

        self._cursor.execute(
            "UPDATE embeds SET description = %s WHERE id = %s", (description, self.id))

        self._db.commit()

    @property
    def color(self) -> int:
        """Returns the color of the embed

        Returns:
            [int]: [The color of the embed]
        """

        self._cursor.execute(
            "SELECT color FROM embeds WHERE id = %s", (self.id,))

        color = self._cursor.fetchone()[0]

        return color

    @color.setter
    def color(self, color: int):
        """Sets the color of the embed

        Args:
            color ([int]): [The color to set]
        """
        # Check if color is valid
        if not isinstance(color, int):
            raise TypeError("color must be an integer")

        if color < 0 or color > 0xffffff:
            raise ValueError("color must be between 0 and 0xffffff")

        # Push to database
        self._cursor.execute(
            "UPDATE embeds SET color = %s WHERE id = %s", (color, self.id))

        self._db.commit()

    @property
    def image(self) -> str:
        """Returns the image of the embed

        Returns:
            [str]: [The image of the embed]
        """

        self._cursor.execute(
            "SELECT image FROM embeds WHERE id = %s", (self.id,))

        image = self._cursor.fetchone()[0]

        return image

    @image.setter
    def image(self, image: str):
        """Sets the image of the embed

        Args:
            image ([str]): [The image to set]
        """
        import requests

        # Check if url is valid
        if not image.startswith("http"):
            raise ValueError("image must be a valid url")

        try:
            requests.get(image)
        except requests.exceptions.RequestException:
            raise ValueError("image must be a valid url")

        # Push to database
        self._cursor.execute(
            "UPDATE embeds SET image = %s WHERE id = %s", (image, self.id))

        self._db.commit()

    @property
    def fields(self) -> list:
        """Returns the fields of the embed

        Returns:
            [list]: [The fields of the embed]
        """

        self._cursor.execute(
            "SELECT name, value FROM embed_fields WHERE embed_id = %s", (self.id,))

        fields = list(self._cursor.fetchall())

        return fields

    @fields.setter
    def fields(self, fields: list):
        """Sets the fields of the embed

        Args:
            fields ([list]): [The fields to set]
        """

        # Check if fields are valid
        if not isinstance(fields, list):
            raise TypeError("fields must be a list")

        for field in fields:
            if not isinstance(field, tuple):
                raise TypeError("fields must be a list of tuples")

            if len(field) != 2:
                raise ValueError("fields must be a list of tuples of length 2")

            if not isinstance(field[0], str):
                raise TypeError("fields must be a list of tuples of strings")

            if not isinstance(field[1], str):
                raise TypeError("fields must be a list of tuples of strings")

        # Push to database
        self._cursor.execute(
            "DELETE FROM embed_fields WHERE embed_id = %s", (self.id,))

        for field in fields:
            self._cursor.execute(
                "INSERT INTO embed_fields (embed_id, name, value) VALUES (%s, %s, %s)", (self.id, field[0], field[1]))

        self._db.commit()

    @property
    def file(self) -> bytes:
        """Returns the file of the embed

        Returns:
            [bytes]: [The file of the embed]
        """

        self._cursor.execute(
            "SELECT file FROM embeds WHERE id = %s", (self.id,))

        file = self._cursor.fetchone()[0]

        return file

    @file.setter
    def file(self, file: bytes):
        """Sets the file of the embed

        Args:
            file ([bytes]): [The file to set]
        """
        # Check if file is valid
        if not isinstance(file, bytes):
            raise TypeError("file must be a bytes object")

        # Push to database
        self._cursor.execute(
            "UPDATE embeds SET file = %s WHERE id = %s", (file, self.id))

        self._db.commit()

    @property
    def file_type(self) -> str:
        """Returns the file type of the embed

        Returns:
            [str]: [The file type of the embed]
        """

        self._cursor.execute(
            "SELECT file_type FROM embeds WHERE id = %s", (self.id,))

        file_type = self._cursor.fetchone()[0]

        return file_type

    @file_type.setter
    def file_type(self, file_type: str):
        """Sets the file type of the embed

        Args:
            file_type ([str]): [The file type to set]
        """

        self._cursor.execute(
            "UPDATE embeds SET file_type = %s WHERE id = %s", (file_type, self.id))

        self._db.commit()

    @property
    def file_name(self) -> str:
        """Returns the file name of the embed

        Returns:
            [str]: [The file name of the embed]
        """

        self._cursor.execute(
            "SELECT file_name FROM embeds WHERE id = %s", (self.id,))

        file_name = self._cursor.fetchone()[0]

        return file_name

    @file_name.setter
    def file_name(self, file_name: str):
        """Sets the file name of the embed

        Args:
            file_name ([str]): [The file name to set]
        """

        self._cursor.execute(
            "UPDATE embeds SET file_name = %s WHERE id = %s", (file_name, self.id))

        self._db.commit()

    def add_field(self, name: str, value: str):
        """Adds a field to the embed

        Args:
            name ([str]): [The name of the field]
            value ([str]): [The value of the field]
        """

        # Check if name is valid
        if not isinstance(name, str):
            raise TypeError("name must be a string")

        if not isinstance(value, str):
            raise TypeError("value must be a string")

        # Push to database
        self._cursor.execute(
            "INSERT INTO embed_fields (embed_id, name, value) VALUES (%s, %s, %s)", (self.id, name, value))

        self._db.commit()


class User:
    def __init__(self, id, db, cursor):
        self.id = id
        self._db = db
        self._cursor = cursor

    @property
    def discord_id(self) -> int:
        """Returns the discord id of the user

        Returns:
            int: [discord_id]
        """

        self._cursor.execute(
            "SELECT discord_id FROM users WHERE id = %s", (self.id,))

        discord_id = self._cursor.fetchone()[0]

        return discord_id

    @property
    def name(self) -> str:
        """Returns the name of the user

        Returns:
            str: [name]
        """

        self._cursor.execute(
            "SELECT name FROM users WHERE id = %s", (self.id,))

        name = self._cursor.fetchone()[0]

        return name

    @property
    def discriminator(self) -> str:
        """Returns the discriminator of the user

        Returns:
            str: [discriminator]
        """

        self._cursor.execute(
            "SELECT discriminator FROM users WHERE id = %s", (self.id,))

        discriminator = self._cursor.fetchone()[0]

        return discriminator

    @property
    def goated(self) -> bool:
        """Returns whether or not the user is goated

        Returns:
            bool: [goated]
        """

        self._cursor.execute(
            "SELECT goated FROM users WHERE id = %s", (self.id,))

        goated = self._cursor.fetchone()[0]

        return goated

    @goated.setter
    def goated(self, value: bool):
        """Sets the goated value of the user

        Args:
            value (bool): [goated]
        """

        self._cursor.execute(
            "UPDATE users SET goated = %s WHERE id = %s", (value, self.id))

        self._db.commit()

    @property
    def rigged(self) -> bool:
        """Returns whether or not the user is rigged

        Returns:
            bool: [rigged]
        """

        self._cursor.execute(
            "SELECT rigged FROM users WHERE id = %s", (self.id,))

        rigged = self._cursor.fetchone()[0]

        return rigged

    @rigged.setter
    def rigged(self, value: bool):
        """Sets the rigged value of the user

        Args:
            value (bool): [rigged]
        """

        self._cursor.execute(
            "UPDATE users SET rigged = %s WHERE id = %s", (value, self.id))

        self._db.commit()

    @property
    def logs(self) -> list:
        """Returns a list of log objects

        Returns:
            list: [list of Log objects]
        """

        self._cursor.execute(
            "SELECT id FROM audit_log WHERE user_id = %s", (self.id,))

        log_ids = self._cursor.fetchall()
        logs = [Log(id[0], self._db, self._cursor) for id in log_ids]

        return logs

    def __repr__(self):
        return f"<User {self.id}, {self.name}{self.discriminator}>"

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id

    def create_embed(self, name) -> 'Embed':
        """Creates an embed for the user

        Args:
            name (str): [The name of the embed]
        """

        self._cursor.execute(
            "INSERT INTO embeds (user_id, name) VALUES (%s, %s)", (self.id, name))

        self._db.commit()

        embed_id = self._cursor.lastrowid

        return Embed(embed_id, self._db, self._cursor)

    def get_logs(self, limit: int = 100, time: datetime.datetime = None, guild=None, channel=None, action=None) -> list:
        """Returns a list of log objects

        Args:
            limit (int, optional): [The limit of logs to return]. Defaults to 100.
            guild (int, optional): [The guild_id to filter by]. Defaults to None.
            channel (int, optional): [The channel_id to filter by]. Defaults to None.
            action (str, optional): [The action to filter by]. Defaults to None.
        """

        query = "SELECT id FROM audit_log WHERE user_id = %s"
        paramaters = (self.id,)

        if guild:
            query = query + " AND guild_id = %s"
            paramaters = paramaters + (guild,)

        if channel:
            query = query + " AND channel_id = %s"
            paramaters = paramaters + (channel,)

        if action:
            query = query + " AND action = %s"
            paramaters = paramaters + (action,)

        if time:
            query = query + " AND time > %s"
            paramaters = paramaters + (time,)

        query = query + " ORDER BY time DESC"

        if limit:
            query = query + " LIMIT %s"
            paramaters = paramaters + (limit,)

        paramaters = paramaters

        self._cursor.execute(query, paramaters)

        log_ids = self._cursor.fetchall()
        logs = [Log(id[0], self._db, self._cursor) for id in log_ids]

        return logs


class Channel:
    def __init__(self, id, db, cursor):
        self.id = id
        self._db = db
        self._cursor = cursor

    @property
    def discord_id(self) -> int:
        """Returns a discord id

        Returns:
            int: [discord_id]
        """

        self._cursor.execute(
            "SELECT discord_id FROM channels WHERE id = %s", (self.id,))

        discord_id = self._cursor.fetchone()[0]

        return discord_id

    @property
    def guild_id(self) -> int:
        """Returns a guild id

        Returns:
            int: [guild_id]
        """

        self._cursor.execute(
            "SELECT guild_id FROM channels WHERE id = %s", (self.id,))

        guild_id = self._cursor.fetchone()[0]

        return guild_id

    @property
    def guild(self) -> 'Guild':
        """Returns a guild

        Returns:
            Guild: [guild]
        """

        return Guild(self.guild_id, self._db, self._cursor)

    @property
    def name(self) -> str:
        """Returns a channel name

        Returns:
            str: [name]
        """

        self._cursor.execute(
            "SELECT name FROM channels WHERE id = %s", (self.id,))

        name = self._cursor.fetchone()[0]

        return name

    @property
    def muted_events(self) -> bool:
        """Returns a bool for if the channel is muted

        Returns:
            bool: [muted_events]
        """

        self._cursor.execute(
            "SELECT muted_events FROM channels WHERE id = %s", (self.id,))

        muted_events = self._cursor.fetchone()[0]

        return muted_events

    @muted_events.setter
    def muted_events(self, value: bool):
        """Sets the muted events value of the channel

        Args:
            value (bool): [muted_events]
        """

        self._cursor.execute(
            "UPDATE channels SET muted_events = %s WHERE id = %s", (value, self.id))

        self._db.commit()

    @property
    def dynamic_voice_channel(self) -> bool:
        """Returns a bool for if the channel is a dynamic voice channel

        Returns:
            bool: [dynamic_voice_channel]
        """

        self._cursor.execute(
            "SELECT dynamic_voice_channel FROM channels WHERE id = %s", (self.id,))

        dynamic_voice_channel = self._cursor.fetchone()[0]

        return dynamic_voice_channel

    @dynamic_voice_channel.setter
    def dynamic_voice_channel(self, value: bool):
        """Sets a bool for if the channel is a dynamic voice channel

        Args:
            value (bool): [value]
        """

        self._cursor.execute(
            "UPDATE channels SET dynamic_voice_channel = %s WHERE id = %s", (value, self.id))

        self._db.commit()

    @property
    def games(self) -> list:
        """Returns a list of games

        Returns:
            list: [games]
        """

        self._cursor.execute(
            "SELECT id FROM games WHERE channel_id = %s", (self.id,))

        game_ids = self._cursor.fetchall()  # [(id,), (id, ) ...]

        games = [Game(game_id[0], self._db, self._cursor)
                 for game_id in game_ids]

        return games

    @property
    def logs(self) -> list:
        """Returns a list of logs

        Returns:
            list: [logs]
        """

        self._cursor.execute(
            "SELECT id FROM audit_log WHERE channel_id = %s", (self.id,))

        log_ids = self._cursor.fetchall()

        logs = [Log(id[0], self._db, self._cursor)
                for id in log_ids]

        return logs

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return f'Channel({self.id, self.name})'


class Guild:
    def __init__(self, id: int, db, cursor):
        self.id = id
        self._db = db
        self._cursor = cursor

    @property
    def discord_id(self) -> int:
        """Returns a discord id

        Returns:
            int: [discord_id]
        """

        self._cursor.execute(
            "SELECT discord_id FROM guilds WHERE id = %s", (self.id,))

        discord_id = self._cursor.fetchone()[0]

        return discord_id

    @property
    def name(self) -> str:
        """Returns a guild name

        Returns:
            str: [name]
        """

        self._cursor.execute(
            "SELECT name FROM guilds WHERE id = %s", (self.id,))

        name = self._cursor.fetchone()[0]

        return name

    @name.setter
    def name(self, name: str):
        """Sets a guild name

        Args:
            name (str): [name]
        """

        self._cursor.execute(
            "UPDATE guilds SET name = %s WHERE id = %s", (name, self.id))
        self._db.commit()

    @property
    def channels(self) -> set:
        """Returns a set of channels

        Returns:
            set: [set of channels]
        """

        self._cursor.execute(
            "SELECT id FROM channels WHERE guild_id = %s", (self.id,))

        channel_ids = self._cursor.fetchall()

        channels = {Channel(id[0], self._db, self._cursor)
                    for id in channel_ids}

        return channels

    @property
    def member_count_channel(self) -> int:
        """Returns a channel id for the channel that
        displays the member count

        Returns:
            int: [channel id]
        """

        self._cursor.execute(
            "SELECT member_count_channel FROM guilds WHERE id = %s",
            (self.id,))

        channel_id = self._cursor.fetchone()[0]

        return channel_id

    @member_count_channel.setter
    def member_count_channel(self, channel_id: int):
        """Sets a channel id for the channel that
        displays the member count

        Args:
            channel_id (int): [channel id]
        """

        self._cursor.execute(
            "UPDATE guilds SET member_count_channel = %s WHERE id = %s",
            (channel_id, self.id))
        self._db.commit()

    @property
    def dynamic_voice_channel_id(self) -> int:
        """Returns a channel id for the channel that
        displays the member count

        Returns:
            int: [channel id]
        """

        self._cursor.execute(
            "SELECT dynamic_voice_channel_id FROM guilds WHERE id = %s",
            (self.id,))

        channel_id = self._cursor.fetchone()[0]

        return channel_id

    @dynamic_voice_channel_id.setter
    def dynamic_voice_channel_id(self, channel_id: int):
        """Sets a channel id for the channel that
        displays the member count

        Args:
            channel_id (int): [channel id]
        """

        self._cursor.execute(
            "UPDATE guilds SET dynamic_voice_channel_id = %s WHERE id = %s",
            (channel_id, self.id))
        self._db.commit()

    @property
    def dynamic_voice_channel_name(self) -> str:
        """Returns a channel name for the channel that
        displays the member count

        Returns:
            str: [channel name]
        """

        self._cursor.execute(
            "SELECT dynamic_voice_channel_name FROM guilds WHERE id = %s",
            (self.id,))

        channel_name = self._cursor.fetchone()[0]

        return channel_name

    @dynamic_voice_channel_name.setter
    def dynamic_voice_channel_name(self, channel_name: str):
        """Sets a channel name for the channel that
        displays the member count

        Args:
            channel_name (str): [channel name]
        """

        self._cursor.execute(
            "UPDATE guilds SET dynamic_voice_channel_name = %s WHERE id = %s",
            (channel_name, self.id))
        self._db.commit()

    @property
    def dynamic_voice_channels(self) -> set:
        """Returns a channel object for the channel that
        displays the member count

        Returns:
            Set: [Set of Channel objects]
        """

        self._cursor.execute(
            "SELECT id FROM channels WHERE guild_id = %s AND dynamic_voice_channel = 1",
            (self.id,))

        channel_ids = self._cursor.fetchall()
        channels = {Channel(id) for id in channel_ids}

        return channels

    @dynamic_voice_channels.setter
    def dynamic_voice_channels(self, channels: set):
        """Sets a channel object for the channel that
        displays the member count

        Args:
            channels (set): [Channel object]
        """

        for channel in self.channels:
            if channel in channels:
                # Set channel to dynamic voice channel if it is in the set
                channel.dynamic_voice_channel = True
            else:
                # Set channel to not dynamic voice channel if it is not in the set
                channel.dynamic_voice_channel = False

    @property
    def member_count_history(self) -> list:
        """Returns a list of member counts over a period of time

        Returns:
            list: [list of member counts]
        """

        self._cursor.execute(
            "SELECT time, count FROM member_count_history WHERE guild_id = %s ORDER BY time DESC",
            (self.id,))

        member_counts = self._cursor.fetchall()

        return member_counts

    @member_count_history.setter
    def member_count_history(self, member_counts: list):
        """Sets a list of member counts over a period of time

        Args:
            member_counts (list): [list of member counts]
        """

        # Check for valid input
        import datetime

        if not isinstance(member_counts, list):
            raise TypeError("member_counts must be a list")

        for member_count in member_counts:
            if not isinstance(member_count, tuple):
                raise TypeError("member_counts must be a list of tuples")

            if len(member_count) != 2:
                raise ValueError(
                    "member_counts must be a list of tuples of length 2")

            if not isinstance(member_count[0], datetime):
                raise TypeError(
                    "member_counts must be a list of tuples of datetime objects")

            if not isinstance(member_count[1], int):
                raise TypeError(
                    "member_counts must be a list of tuples of ints")

        # Delete old member count history
        self._cursor.execute(
            "DELETE FROM member_count_history WHERE guild_id = %s", (self.id,))

        # Insert new member count history
        for member_count in member_counts:
            self._cursor.execute(
                "INSERT INTO member_count_history (guild_id, time, count) VALUES (%s, %s, %s)",
                (self.id, member_count[0], member_count[1]))

        self._db.commit()

    @property
    def slash_commands(self) -> bool:
        """Returns whether or not slash commands are enabled

        Returns:
            bool: [True if enabled, False otherwise]
        """

        self._cursor.execute(
            "SELECT slash_commands FROM guilds WHERE id = %s",
            (self.id,))

        enabled = self._cursor.fetchone()[0]

        return enabled

    @slash_commands.setter
    def slash_commands(self, enabled: bool):
        """Sets whether or not slash commands are enabled

        Args:
            enabled (bool): [True if enabled, False otherwise]
        """

        self._cursor.execute(
            "UPDATE guilds SET slash_commands = %s WHERE id = %s",
            (enabled, self.id))

        self._db.commit()

    @property
    def logs(self) -> list:
        """Returns a list of log objects

        Returns:
            list: [list of Log objects]
        """

        self._cursor.execute(
            "SELECT id FROM audit_log WHERE guild_id = %s", (self.id,))

        log_ids = self._cursor.fetchall()
        logs = [Log(id[0], self._db, self._cursor) for id in log_ids]

        return logs

    @property
    def auto_mod(self) -> bool:
        """Returns AutoMod object

        Returns:
            AutoMod: [AutoMod object]
        """

        self._cursor.execute(
            "SELECT id FROM auto_mod_config WHERE guild_id = %s", (self.id,))

        auto_mod_id = self._cursor.fetchone()[0]

        return AutoMod(auto_mod_id, self._db, self._cursor)

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return f'Guild({self.id, self.name})'

    def __eq__(self, other):
        return self.id == other.id

    def get_channel(self, discord_id: int) -> 'Channel':
        """Returns a channel object based on a discord id

        Args:
            discord_id (int): [discord id]

        Returns:
            Channel: [Channel object]
        """

        self._cursor.execute(
            "SELECT id FROM channels WHERE guild_id = %s AND discord_id = %s",
            (self.id, discord_id))

        try:
            channel_id = self._cursor.fetchone()[0]
        except TypeError:
            raise EntryNotFound("Channel is not a part of this guild")

        return Channel(channel_id, self._db, self._cursor)

    def add_channel(self, discord_id, name, **kwargs):
        """Adds a channel to the guild

        Args:
            channel (Channel): [Channel object]
        """

        self._cursor.execute(
            "SELECT id FROM channels WHERE guild_id = %s AND discord_id = %s", (self.id, discord_id))

        if len(self._cursor.fetchall()) != 0:
            raise EntryAlreadyExists("Channel already exists in this guild")

        # Optional args
        dynamic_voice_channel = kwargs.get('dynamic_voice_channel', False)

        self._cursor.execute(
            "INSERT INTO channels (guild_id, discord_id, name, dynamic_voice_channel) VALUES (%s, %s, %s, %s)",
            (self.id, discord_id, name, dynamic_voice_channel))
        self._db.commit()

        return Channel(self._cursor.lastrowid, self._db, self._cursor)

    def remove_channel(self, discord_id):
        """Removes a channel from the guild

        Args:
            channel (Channel): [Channel object]
        """

        self._cursor.execute(
            "DELETE FROM channels WHERE guild_id = %s AND discord_id = %s",
            (self.id, discord_id))
        self._db.commit()


class Data:
    def __init__(self):
        load_dotenv()

        self._db = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            passwd=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
        )

        self._cursor = self._db.cursor(buffered=True)

    @property
    def guild_discord_ids(self) -> list:
        """Returns a list of guild ids

        Returns:
            list: [list of guild ids]
        """

        self._cursor.execute("SELECT discord_id FROM guilds")

        discord_ids = self._cursor.fetchall()
        discord_ids = [discord_id[0]
                       for discord_id in discord_ids]  # Convert to ints

        return discord_ids

    @property
    def guilds(self) -> list:
        """Returns a set of guild objects

        Returns:
            List: [List of Guild objects]
        """

        self._cursor.execute(
            "SELECT id FROM guilds")

        guild_ids = self._cursor.fetchall()
        guilds = [Guild(id[0], self._db, self._cursor) for id in guild_ids]

        return guilds

    @property
    def enabled_slash(self) -> list:
        """Returns a list of guild ids that have slash commands enabled

        Returns:
            list: [list of guild ids]
        """

        self._cursor.execute(
            "SELECT discord_id FROM guilds WHERE slash_commands = 1")

        discord_ids = self._cursor.fetchall()
        discord_ids = [discord_id[0]
                       for discord_id in discord_ids]  # Convert to ints

        return discord_ids

    @property
    def cogs(self) -> list:
        """Returns a list of cog objects

        Returns:
            list: [list of cog objects]
        """

        self._cursor.execute("SELECT id FROM cogs")

        cog_ids = self._cursor.fetchall()
        cogs = [Cog(id[0], self._db, self._cursor) for id in cog_ids]

        return cogs

    @property
    def logs(self) -> list:
        """Returns a list of log objects

        Returns:
            list: [list of log objects]
        """

        self._cursor.execute("SELECT id FROM audit_log")

        log_ids = self._cursor.fetchall()
        logs = [Log(id[0], self._db, self._cursor) for id in log_ids]

        return logs

    def get_guild(self, discord_id: int) -> Guild:
        """Returns Guild object from database

        Args:
            discord_id ([int]): [Id discord associates with each guild]

        Returns:
            Guild: [Guild object]
        """

        self._cursor.execute(
            "SELECT id FROM guilds WHERE discord_id = %s", (discord_id,))

        try:
            guild_id = self._cursor.fetchone()[0]
        except TypeError:
            raise EntryNotFound("Guild does not exist in the database")

        return Guild(guild_id, self._db, self._cursor)

    def add_guild(self, discord_id: int, name: str):
        """Adds a guild to the database

        Args:
            discord_id (int): [Id discord associates with each guild]
            name (str): [Name of the guild]

        Returns:
            Guild: [Guild object]
        """
        # Check if guild is already in the database
        self._cursor.execute(
            "SELECT * FROM guilds WHERE discord_id = %s", (discord_id,))

        if len(self._cursor.fetchall()) != 0:
            raise EntryAlreadyExists(
                f"Guild with id {discord_id} already exists in the database")

        # Insert new guild
        self._cursor.execute(
            "INSERT INTO guilds (discord_id, name) VALUES (%s, %s)",
            (discord_id, name))

        guild = Guild(self._cursor.lastrowid, self._db, self._cursor)

        self._cursor.execute(
            "INSERT INTO auto_mod_config (guild_id) VALUES (%s)", (guild.id,))

        self._db.commit()

        return guild

    def get_channel(self, discord_id: int) -> Channel:
        """Returns Channel object from database

        Args:
            discord_id ([int]): [Id discord associates with each channel]
        """

        self._cursor.execute(
            "SELECT id FROM channels WHERE discord_id = %s", (discord_id,))

        try:
            channel_id = self._cursor.fetchone()[0]
        except TypeError:
            raise EntryNotFound("Channel does not exist in the database")

        return Channel(channel_id, self._db, self._cursor)

    def add_channel(self, discord_id: int, name: str, **kwargs):
        """Adds a channel to the database

        Args:
            discord_id (int): [Id discord associates with each channel]
            name (str): [Name of the channel]
        """
        # Check if channel is already in the database
        self._cursor.execute(
            "SELECT * FROM channels WHERE discord_id = %s", (discord_id,))

        if len(self._cursor.fetchall()) != 0:
            raise EntryAlreadyExists(
                f"Channel with id {discord_id} already exists in the database")

        # Optional args
        dynamic_voice_channel = kwargs.get('dynamic_voice_channel', False)

        # Insert new channel
        self._cursor.execute(
            "INSERT INTO channels (discord_id, name, dynamic_voice_channel) VALUES (%s, %s, %s)",
            (discord_id, name, dynamic_voice_channel))
        self._db.commit()

        channel = Channel(self._cursor.lastrowid, self._db, self._cursor)

        return channel

    def get_user(self, discord_id: int) -> User:
        """Returns User object from database

        Args:
            discord_id ([int]): [Id discord associates with each user]

        Returns:
            User: [User object]
        """

        self._cursor.execute(
            "SELECT id FROM users WHERE discord_id = %s", (discord_id,))

        try:
            user_id = self._cursor.fetchone()[0]
        except TypeError:
            raise EntryNotFound("User does not exist in the database")

        return User(user_id, self._db, self._cursor)

    def add_user(self, discord_id: int, name: str, discriminator: str):
        """Adds a user to the database

        Args:
            discord_id (int): [Id discord associates with each user]
            name (str): [Name of the user]
            discriminator (str): [Discriminator of the user]
        """
        # Check if user is already in the database
        self._cursor.execute(
            "SELECT * FROM users WHERE discord_id = %s", (discord_id,))

        if len(self._cursor.fetchall()) != 0:
            raise EntryAlreadyExists(
                f"User with id {discord_id} already exists in the database")

        # Insert new user
        self._cursor.execute(
            "INSERT INTO users (discord_id, name, discriminator) VALUES (%s, %s, %s)",
            (discord_id, name, discriminator))
        self._db.commit()

        user = User(self._cursor.lastrowid, self._db, self._cursor)

        return user

    def get_cog(self, name: str) -> Cog:
        """Returns Cog object from database

        Args:
            name (str): [Name of the cog]
        """

        self._cursor.execute("SELECT id FROM cogs WHERE name = %s", (name,))

        try:  # Check if cog exists
            cog_id = self._cursor.fetchone()[0]
        except TypeError:
            raise EntryNotFound("Cog does not exist in the database")

        return Cog(cog_id, self._db, self._cursor)

    def add_log(self, action: str, extra: str = None, **kwargs):
        """Adds a log to the database

        Args:
            action (str): [Action that was taken]
            extra (str): [Extra information]
            ctx (Context): [Discord Context]
            **kwargs: Other ways to set information
        """
        import datetime

        # Optional args
        user_id = kwargs.get('user_id', None)
        guild_id = kwargs.get('guild_id', None)
        channel_id = kwargs.get('channel_id', None)
        message_id = kwargs.get('message_id', None)
        message_text = kwargs.get('message_text', None)

        # Get current time
        time = datetime.datetime.now()

        # Insert new log
        self._cursor.execute(
            "INSERT INTO audit_log (time, action, extra, user_id, guild_id, channel_id, message_id, message_text) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (time, action, extra, user_id, guild_id, channel_id, message_id, message_text))
        self._db.commit()


if __name__ == "__main__":
    data = Data()
