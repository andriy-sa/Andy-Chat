from orator.migrations import Migration


class CreateRoomMembersTable(Migration):

    def up(self):
        """
        Run the migrations.
        """
        with self.schema.create('room_members') as table:
            table.increments('id')
            table.integer('room_id').unsigned().index()
            table.foreign('room_id').references('id').on('rooms').on_delete('CASCADE')
            table.integer('user_id').unsigned().index()
            table.foreign('user_id').references('id').on('users').on_delete('CASCADE')
            table.timestamps()
            table.unique(['room_id','user_id'])

    def down(self):
        """
        Revert the migrations.
        """
        self.schema.drop('room_members')
