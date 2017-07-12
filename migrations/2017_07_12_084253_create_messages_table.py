from orator.migrations import Migration


class CreateMessagesTable(Migration):

    def up(self):
        """
        Run the migrations.
        """
        with self.schema.create('messages') as table:
            table.big_increments('id')
            table.integer('sender_id').unsigned().index()
            table.foreign('sender_id').references('id').on('users').on_delete('CASCADE')
            table.integer('room_id').unsigned().index()
            table.foreign('room_id').references('id').on('rooms').on_delete('CASCADE')
            table.text('message')
            table.timestamps()

    def down(self):
        """
        Revert the migrations.
        """
        self.schema.drop('messages')
