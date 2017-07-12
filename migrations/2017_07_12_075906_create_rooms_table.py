from orator.migrations import Migration


class CreateRoomsTable(Migration):
    def up(self):
        """
        Run the migrations.
        """
        with self.schema.create('rooms') as table:
            table.increments('id')
            table.boolean('is_group').default(0)
            table.integer('user_id').unsigned().index().nullable().default(None)
            table.foreign('user_id').references('id').on('users').on_delete('CASCADE')
            table.timestamps()

    def down(self):
        self.schema.drop('rooms')
