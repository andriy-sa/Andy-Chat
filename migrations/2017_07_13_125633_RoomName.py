from orator.migrations import Migration


class RoomName(Migration):

    def up(self):
        with self.schema.table('rooms') as table:
            table.string('name').nullable().default(None)

    def down(self):
        with self.schema.table('rooms') as table:
            table.drop_column('name')
