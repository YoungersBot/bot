class UpdateTables:
    subscriptions_add_date_columns = """
        ALTER TABLE subscriptions
        ADD COLUMN departure_date DATE DEFAULT NULL,
        ADD COLUMN return_date DATE DEFAULT NULL;
        """
