from orator.migrations import Migration


class LastReadMessage(Migration):

    def up(self):

        with self.schema.table('room_members') as table:
            table.big_integer('last_read_message').unsigned().index().nullable().default(None)
            table.foreign('last_read_message').references('id').on('messages').on_delete('CASCADE')

    def down(self):

        with self.schema.table('room_members') as table:
            table.drop_column('last_read_message')
