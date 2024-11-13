class Conversion:
    @staticmethod
    def conversion_time(duration):
        # Convert adjusted_duration to minutes or hours
        total_seconds = int(duration.total_seconds())
        hours = total_seconds // 3600  # Calculate full hours
        minutes = (total_seconds % 3600) // 60  # Calculate remaining minutes
        seconds = total_seconds % 60  # Calculate remaining seconds

        # Helper function to make the word singular or plural
        def singular_or_plural(value, word):
            if value == 1:
                return word  # Singular
            else:
                return word + 's'  # Plural

        # Format the duration in a more readable format
        if hours > 0:
            if minutes > 0 and seconds > 0:
                return f"{hours} {singular_or_plural(hours, 'hour')}, {minutes} {singular_or_plural(minutes, 'minute')}, and {seconds} {singular_or_plural(seconds, 'second')}"
            elif minutes > 0:
                return f"{hours} {singular_or_plural(hours, 'hour')} and {minutes} {singular_or_plural(minutes, 'minute')}"
            elif seconds > 0:
                return f"{hours} {singular_or_plural(hours, 'hour')} and {seconds} {singular_or_plural(seconds, 'second')}"
            else:
                return f"{hours} {singular_or_plural(hours, 'hour')}"
        elif minutes > 0:
            return f"{minutes} {singular_or_plural(minutes, 'minute')} and {seconds} {singular_or_plural(seconds, 'second')}"
        else:
            return f"{seconds} {singular_or_plural(seconds, 'second')}"  # If it's less than a minute