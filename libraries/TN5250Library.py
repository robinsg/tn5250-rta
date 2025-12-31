import subprocess
import time
import os
import datetime
from robot.api import logger

class TN5250Library:
    """
    Robot Framework library for headless TN5250 testing via tmux.
    Supports SSL connections natively.
    """

    def __init__(self, verbose=False):
        """Initialize the TN5250Library.

        Args:
            verbose (bool or str, optional): Enable verbose console output.
                Accepts boolean values or string representations like "true", "1", "yes", "y".
                Defaults to False.

        Returns:
            None
        """
        # Robot may pass boolean-like strings; normalize
        try:
            self.verbose = str(verbose).lower() in ("true", "1", "yes", "y")
        except Exception:
            self.verbose = False
        self.session_name = "robot_tn5250_session"

    def set_verbose(self, verbose=True):
        """Keyword to enable/disable verbose console output.

        Args:
            verbose (bool or str, optional): Enable verbose console output.
                Accepts boolean values or string representations like "true", "1", "yes", "y".
                Defaults to True.

        Returns:
            None

        Examples:
            Set TN5250 Verbose    True
        """
        try:
            self.verbose = str(verbose).lower() in ("true", "1", "yes", "y")
        except Exception:
            self.verbose = False
        logger.info(f"TN5250Library verbose set to {self.verbose}")
        if self.verbose:
            logger.console(f"TN5250Library verbose set to {self.verbose}")

    def _log(self, message):
        """Internal logging method that logs to info and optionally to console.

        Args:
            message (str): The message to log.

        Returns:
            None
        """
        logger.info(message)
        if getattr(self, "verbose", False):
            logger.console(message)

    def start_tn5250_session(self, hostname, ssl, devname=None, map=285):
        """Starts tn5250 in a background tmux session.

        Creates a headless tmux session with standard 80x24 screen dimensions
        and establishes a TN5250 connection to the specified hostname.

        Args:
            hostname (str): The hostname or IP address to connect to.
            ssl (bool or str): If True, connects using SSL ('ssl:hostname' format).
                Accepts boolean values or string representations.
            devname (str, optional): The device name to use for the connection.
                If provided, sets the DEVNAME environment variable. Defaults to None.
            map (int, optional): The character map code to use. Defaults to 285.

        Returns:
            None

        Raises:
            subprocess.CalledProcessError: If tmux session creation fails.
        """
        self.stop_tn5250_session() # Cleanup any old sessions
        
        # Construct the command: 'tn5250 ssl:172.16.8.41'
        prefix = "ssl:" if ssl else ""
        
        cmd = f"tn5250 {prefix}{hostname} map={map}"
        if devname is not None:
            cmd += f" env.DEVNAME={devname}"
        
        self._log(f"Starting session: {cmd}")
        
        # Start headless tmux session (-d) with standard 80x24 screen
        subprocess.run([
            "tmux", "new-session", "-d",
            "-s", self.session_name,
            "-x", "80", "-y", "24",
            cmd
        ], check=True)
        
        time.sleep(3) # Give SSL handshake a moment to finish

    def stop_tn5250_session(self):
        """Kills the tmux session.

        Terminates the active TN5250 tmux session. Errors are silently ignored
        if the session doesn't exist.

        Returns:
            None
        """
        self._log(f"Killing tmux session: {self.session_name}")
        subprocess.run([
            "tmux", "kill-session", "-t", self.session_name
        ], stderr=subprocess.DEVNULL)

    def send_text(self, text):
        """Types text into the terminal.

        Sends the specified text to the active TN5250 session as keyboard input.

        Args:
            text (str): The text to type into the terminal.

        Returns:
            None

        Raises:
            subprocess.CalledProcessError: If sending keys to tmux fails.
        """
        self._log(f"Typing: '{text}'")
        subprocess.run(["tmux", "send-keys", "-t", self.session_name, text], check=True)

    def send_special_key(self, key_name):
        """Sends special keys to the terminal.

        Sends special keys like Enter, Tab, function keys, or Backspace to the
        active TN5250 session. Includes a 0.5 second delay for screen refresh.

        Args:
            key_name (str): The name of the special key to send.
                Examples: "Enter", "Tab", "F3", "Backspace", "F6", etc.

        Returns:
            None

        Raises:
            subprocess.CalledProcessError: If sending keys to tmux fails.
        """
        self._log(f"Sending Key: {key_name}")
        subprocess.run(["tmux", "send-keys", "-t", self.session_name, key_name], check=True)
        time.sleep(0.5) # Wait for screen refresh

    def screen_should_contain(self, expected_text, timeout=10):
        """Waits for text to appear on screen.

        Polls the TN5250 screen content until the expected text is found or
        timeout is reached. If verbose mode is enabled, displays the matching
        screen content. On failure, dumps the final screen content to console.

        Args:
            expected_text (str): The text to search for on the screen.
            timeout (int or str, optional): Maximum time in seconds to wait for
            bool: True if the text is found within the timeout period. This method
            never returns False or None; on timeout it raises an AssertionError.
            never returns False or None; on timeout it raises an AssertionError.

        Returns:
            bool: True if the text is found within the timeout period.

        Raises:
            AssertionError: If the timeout is reached without finding the expected text.
        """
        start_time = time.time()
        while time.time() - start_time < int(timeout):
            # Capture current screen content
            result = subprocess.run([
                "tmux", "capture-pane", "-p", "-t", self.session_name
            ], capture_output=True, text=True)
            if expected_text in result.stdout:
                self._log(f"Found text: '{expected_text}'")
                if self.verbose:
                    # Show the matching screen output for debug
                    logger.console("--- SCREEN (MATCH) ---")
                    logger.console(result.stdout)
                return True
            time.sleep(0.5)
            
        # Log failure
        self._log("--- SCREEN DUMP (FAILURE) ---")
        logger.console(result.stdout)
        raise AssertionError(f"Timeout: Text '{expected_text}' not found on screen.")

    def capture_screen(self, filename=None, image=False):
        """Captures the current TN5250 screen to a text file.

        Saves the current screen content to a text file under `results/screenshots`.
                If None, generates a timestamp-based name like "screen_20231225_120000".
                <timestamp> uses the "%Y%m%d_%H%M%S" format (e.g., "screen_20231225_120000").
                <timestamp> uses the "%Y%m%d_%H%M%S" format (e.g., "screen_20231225_120000").
        the screen as a PNG image.

        Args:
            filename (str, optional): Base name for the output file (without extension).
                If None, generates a timestamp-based name like "screen_20231225_120000".
                Defaults to None.
            image (bool or str, optional): If True, also generate a PNG image of the screen
                using ImageMagick. Accepts boolean values or string representations like
                "true", "1", "yes", "y". Defaults to False.

        Returns:
            str: The full path to the saved text file.

        Raises:
            subprocess.CalledProcessError: If tmux capture-pane fails.
        """
        # Normalize image flag (Robot passes strings sometimes)
        image_flag = False
        try:
            image_flag = str(image).lower() in ("true", "1", "yes", "y")
        except Exception:
            image_flag = False

        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Use LPAR-specific screenshot directory if LPAR_NAME is set
        lpar_name = os.environ.get("LPAR_NAME", "")
        if lpar_name:
            out_dir = os.path.join("results", lpar_name, "screenshots")
        else:
            out_dir = os.path.join("results", "screenshots")
        os.makedirs(out_dir, exist_ok=True)

        base = filename if filename else f"screen_{ts}"
        txt_path = os.path.join(out_dir, base + ".txt")

        result = subprocess.run([
            "tmux", "capture-pane", "-p", "-t", self.session_name
        ], capture_output=True, text=True)

        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(result.stdout)

        self._log(f"Saved screen text to {txt_path}")

        if image_flag:
            png_path = os.path.join(out_dir, base + ".png")
            try:
                proc = subprocess.run(
                    [
                        "convert",
                        "-background",
                        "black",
                        "-fill",
                        "white",
                        "-font",
                        "DejaVu-Sans-Mono",
                        "-pointsize",
                        "12",
                        f"text:{txt_path}",
                        png_path,
                    ],
                    text=True,
                    capture_output=True,
                )
                if proc.returncode == 0:
                    self._log(f"Saved screen image to {png_path}")
                else:
                    self._log(f"ImageMagick convert failed: {proc.stderr}")
            except FileNotFoundError:
                self._log("ImageMagick `convert` not found; skipping image.")

        return txt_path

    def get_screen_text_at_position(self, row, start_col, end_col):
        """Get text at a specific position on the TN5250 screen.

        Extracts text from the screen at the specified row and column range.
        Rows and columns are 1-indexed (row 1 is the first row, column 1 is the first column).

        Args:
            row (int or str): The row number (1-indexed) to extract text from.
            start_col (int or str): The starting column (1-indexed, inclusive).
            end_col (int or str): The ending column (1-indexed, inclusive).

        Returns:
            str: The extracted text from the specified position, with leading/trailing whitespace removed.

        Raises:
            subprocess.CalledProcessError: If tmux capture-pane fails.
            IndexError: If the row or column positions are out of range.
        """
        row = int(row)
        start_col = int(start_col)
        end_col = int(end_col)

        result = subprocess.run([
            "tmux", "capture-pane", "-p", "-t", self.session_name
        ], capture_output=True, text=True, check=True)

        lines = result.stdout.split('\n')
        
        if row < 1 or row > len(lines):
            raise IndexError(f"Row {row} is out of range (1-{len(lines)})")
        
        # Convert to 0-indexed for Python
        line = lines[row - 1]
        
        # Ensure we have enough columns
        if start_col < 1:
            raise IndexError(f"Start column {start_col} is out of range (must be >= 1)")
        if end_col > len(line):
            raise IndexError(f"End column {end_col} is out of range (line length is {len(line)})")
        
        # Extract text (convert to 0-indexed, end_col is inclusive)
        text = line[start_col - 1:end_col]
        text = text.strip()
        
        self._log(f"Extracted text at row {row}, cols {start_col}-{end_col}: '{text}'")
        return text

    def screen_should_contain_at_position(self, row, start_col, end_col, expected_text):
        """Verify that specific text appears at a position on the screen.

        Checks if the expected text matches the text at the specified position.
        Comparison is case-sensitive.

        Args:
            row (int or str): The row number (1-indexed) to check.
            start_col (int or str): The starting column (1-indexed, inclusive).
            end_col (int or str): The ending column (1-indexed, inclusive).
            expected_text (str): The expected text at that position.

        Returns:
            bool: True if the text matches.

        Raises:
            AssertionError: If the text does not match the expected value.
        """
        actual_text = self.get_screen_text_at_position(row, start_col, end_col)
        
        if actual_text != expected_text:
            raise AssertionError(
                f"Text mismatch at row {row}, cols {start_col}-{end_col}:\n"
                f"Expected: '{expected_text}'\n"
                f"Actual: '{actual_text}'"
            )
        
        self._log(f"✓ Text matches at row {row}, cols {start_col}-{end_col}: '{expected_text}'")
        return True

    def verify_numeric_value_greater_than(self, row, start_col, end_col, min_value):
        """Verify that a numeric value at a position is greater than a minimum value.

        Extracts text from the specified position, converts it to an integer,
        and verifies it is greater than the minimum value.

        Args:
            row (int or str): The row number (1-indexed) to check.
            start_col (int or str): The starting column (1-indexed, inclusive).
            end_col (int or str): The ending column (1-indexed, inclusive).
            min_value (int or str): The minimum value (exclusive).

        Returns:
            bool: True if the numeric value is greater than min_value.

        Raises:
            AssertionError: If the value is not greater than min_value.
            ValueError: If the extracted text cannot be converted to an integer.
        """
        text = self.get_screen_text_at_position(row, start_col, end_col)
        min_value = int(min_value)
        
        try:
            actual_value = int(text)
        except ValueError:
            raise ValueError(f"Cannot convert '{text}' to integer at row {row}, cols {start_col}-{end_col}")
        
        if actual_value <= min_value:
            raise AssertionError(
                f"Value at row {row}, cols {start_col}-{end_col} is not greater than {min_value}:\n"
                f"Expected: > {min_value}\n"
                f"Actual: {actual_value}"
            )
        
        self._log(f"✓ Value {actual_value} > {min_value} at row {row}, cols {start_col}-{end_col}")
        return True

    def count_occurrences_in_lines(self, text, start_row, end_row, case_sensitive=True):
        """Count occurrences of text in a specific range of lines.

        Searches for the specified text in lines from start_row to end_row (inclusive)
        and returns the count of occurrences.

        Args:
            text (str): The text to search for.
            start_row (int or str): The starting row (1-indexed, inclusive).
            end_row (int or str): The ending row (1-indexed, inclusive).
            case_sensitive (bool or str, optional): If True, search is case-sensitive.
                Accepts boolean values or string representations like "true", "1", "yes", "y".
                Defaults to True.

        Returns:
            int: The number of occurrences found.

        Raises:
            subprocess.CalledProcessError: If tmux capture-pane fails.
        """
        start_row = int(start_row)
        end_row = int(end_row)
        
        # Normalize case_sensitive flag
        if isinstance(case_sensitive, str):
            case_sensitive = case_sensitive.lower() not in ("false", "0", "no", "n")
        elif not isinstance(case_sensitive, bool):
            case_sensitive = True

        result = subprocess.run([
            "tmux", "capture-pane", "-p", "-t", self.session_name
        ], capture_output=True, text=True, check=True)

        lines = result.stdout.split('\n')
        
        # Extract the relevant line range
        relevant_lines = lines[start_row - 1:end_row]
        
        count = 0
        search_text = text if case_sensitive else text.upper()
        
        for line in relevant_lines:
            search_line = line if case_sensitive else line.upper()
            count += search_line.count(search_text)
        
        self._log(f"Found {count} occurrence(s) of '{text}' in rows {start_row}-{end_row}")
        return count

    def verify_occurrence_count(self, text, start_row, end_row, expected_count, case_sensitive=True):
        """Verify that text appears a specific number of times in a line range.

        Counts occurrences of text in the specified line range and verifies
        it matches the expected count.

        Args:
            text (str): The text to search for.
            start_row (int or str): The starting row (1-indexed, inclusive).
            end_row (int or str): The ending row (1-indexed, inclusive).
            expected_count (int or str): The expected number of occurrences.
            case_sensitive (bool or str, optional): If True, search is case-sensitive.
                Accepts boolean values or string representations like "true", "1", "yes", "y".
                Defaults to True.

        Returns:
            bool: True if the count matches.

        Raises:
            AssertionError: If the count does not match the expected value.
        """
        expected_count = int(expected_count)
        actual_count = self.count_occurrences_in_lines(text, start_row, end_row, case_sensitive)
        
        if actual_count != expected_count:
            raise AssertionError(
                f"Occurrence count mismatch for '{text}' in rows {start_row}-{end_row}:\n"
                f"Expected: {expected_count}\n"
                f"Actual: {actual_count}"
            )
        
        self._log(f"✓ Found {actual_count} occurrence(s) of '{text}' in rows {start_row}-{end_row}")
        return True

    def verify_all_values_on_same_line(self, values_list):
        """Verify that all values in a comma-separated list appear on the same line.

        Searches the screen for a line that contains all the specified values.

        Args:
            values_list (str): Comma-separated list of values to search for (e.g., "VALUE1,VALUE2").

        Returns:
            bool: True if all values are found on the same line.

        Raises:
            AssertionError: If no line contains all the values.
        """
        values = [v.strip() for v in values_list.split(',')]
        
        result = subprocess.run([
            "tmux", "capture-pane", "-p", "-t", self.session_name
        ], capture_output=True, text=True, check=True)

        lines = result.stdout.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            if all(value in line for value in values):
                self._log(f"✓ All values {values} found on line {line_num}: '{line.strip()}'")
                return True
        
        # Show only first 10 lines of screen content in error for readability
        screen_preview = '\n'.join(lines[:10])
        if len(lines) > 10:
            screen_preview += f"\n... ({len(lines) - 10} more lines)"
        
        raise AssertionError(
            f"No line found containing all values: {values}\n"
            f"Screen preview (first 10 lines):\n{screen_preview}"
        )
