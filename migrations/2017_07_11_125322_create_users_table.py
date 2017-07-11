from orator.migrations import Migration


class CreateUsersTable(Migration):

    def up(self):
        """
        Run the migrations.
        """
        with self.schema.create('users') as table:
            table.increments('id')
            table.string('email').unique()
            table.string('first_name')
            table.string('last_name')
            table.string('avatar').default(None).nullable()
            table.string('password')
            table.boolean('is_active').default(1)
            table.timestamps()

    def down(self):
        """
        Revert the migrations.
        """
        self.schema.drop('users')
