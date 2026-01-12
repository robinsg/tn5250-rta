import subprocess
import time
import os
import datetime
from robot.api import logger
from robot.utils import Secret

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
        
        # Normalize ssl parameter (Robot may pass strings like "0", "1", "true", etc.)
        try:
            ssl_enabled = str(ssl).lower() in ("true", "1", "yes", "y")
        except Exception:
            ssl_enabled = False
        
        # Construct the command: 'tn5250 ssl:172.16.8.41'
        prefix = "ssl:" if ssl_enabled else ""
        
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
        Supports Robot Framework Secret type for passwords - the Secret will be
        logged as '<secret>' but the actual value will be sent to the terminal.

        Args:
            text (str or Secret): The text to type into the terminal.
                Can be a regular string or a Robot Framework Secret object.

        Returns:
            None

        Raises:
            subprocess.CalledProcessError: If sending keys to tmux fails.
        """
        # Extract actual value from Secret if needed, but log obfuscated version
        actual_text = text.value if isinstance(text, Secret) else text
        
        self._log(f"Typing: '{text}'")
        subprocess.run(["tmux", "send-keys", "-t", self.session_name, actual_text], check=True)

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

    def screen_should_contain_at_position(self, row, start_col, end_col, expected_text):
        """Verifies that specific text appears at a given row and column position.

        Extracts text from the screen at the specified coordinates and compares it
        to the expected value. This is useful for validating field values at known
        positions on 5250 screens.

        Args:
            row (int or str): The row number (1-based) where the text should appear.
            start_col (int or str): The starting column number (1-based) of the text.
            end_col (int or str): The ending column number (1-based) of the text.
            expected_text (str): The expected text at the specified position.

        Returns:
            None

        Raises:
            AssertionError: If the actual text doesn't match the expected text.
            subprocess.CalledProcessError: If tmux capture-pane fails.

        Examples:
            Screen Should Contain At Position    14    34    36    100
            Screen Should Contain At Position    7     35    36    ${QSECURITY}
        """
        # Convert parameters to integers
        row = int(row)
        start_col = int(start_col)
        end_col = int(end_col)
        
        # Capture current screen content
        result = subprocess.run([
            "tmux", "capture-pane", "-p", "-t", self.session_name
        ], capture_output=True, text=True, check=True)
        
        # Split into lines (row is 1-based)
        lines = result.stdout.splitlines()
        
        # Validate row number
        if row < 1 or row > len(lines):
            raise AssertionError(
                f"Row {row} out of range (screen has {len(lines)} lines)"
            )
        
        # Extract the line (convert to 0-based index)
        line = lines[row - 1]
        
        # Extract text at specified columns (convert to 0-based indices)
        # Columns are 1-based, so subtract 1
        actual_text = line[start_col - 1:end_col].strip()
        expected_text_str = str(expected_text).strip()
        
        self._log(
            f"Position check: Row {row}, Cols {start_col}-{end_col}: "
            f"Expected='{expected_text_str}', Actual='{actual_text}'"
        )
        
        if actual_text != expected_text_str:
            # On failure, show more context
            self._log("--- SCREEN DUMP (POSITION MISMATCH) ---")
            logger.console(result.stdout)
            raise AssertionError(
                f"Text at position (row={row}, cols={start_col}-{end_col}) does not match.\n"
                f"Expected: '{expected_text_str}'\n"
                f"Actual:   '{actual_text}'"
            )

    def verify_occurrence_count(self, search_text, start_row, end_row, expected_count, case_sensitive=True):
        """Verifies the number of times text appears within a row range.

        Counts how many times the search text appears in the specified row range
        and compares it to the expected count.

        Args:
            search_text (str): The text to search for.
            start_row (int or str): The starting row number (1-based).
            end_row (int or str): The ending row number (1-based).
            expected_count (int or str): The expected number of occurrences.
            case_sensitive (bool or str, optional): Whether the search should be
                case-sensitive. Defaults to True.

        Returns:
            None

        Raises:
            AssertionError: If the actual count doesn't match the expected count.
            subprocess.CalledProcessError: If tmux capture-pane fails.

        Examples:
            Verify Occurrence Count    ${HOST}    3    7    3    case_sensitive=False
            Verify Occurrence Count    ${NETSTAT}    10    20    1
        """
        # Convert parameters
        start_row = int(start_row)
        end_row = int(end_row)
        expected_count = int(expected_count)
        
        # Normalize case_sensitive parameter
        try:
            case_sensitive_flag = str(case_sensitive).lower() not in ("false", "0", "no", "n")
        except Exception:
            case_sensitive_flag = True
        
        # Capture current screen content
        result = subprocess.run([
            "tmux", "capture-pane", "-p", "-t", self.session_name
        ], capture_output=True, text=True, check=True)
        
        # Split into lines
        lines = result.stdout.splitlines()
        
        # Validate row range
        if start_row < 1 or start_row > len(lines):
            raise AssertionError(f"Start row {start_row} out of range (screen has {len(lines)} lines)")
        if end_row < 1 or end_row > len(lines):
            raise AssertionError(f"End row {end_row} out of range (screen has {len(lines)} lines)")
        
        # Count occurrences in the specified row range
        count = 0
        search_str = str(search_text)
        
        for row_num in range(start_row, end_row + 1):
            line = lines[row_num - 1]  # Convert to 0-based index
            
            if case_sensitive_flag:
                count += line.count(search_str)
            else:
                count += line.lower().count(search_str.lower())
        
        self._log(
            f"Occurrence count: Rows {start_row}-{end_row}: "
            f"Expected={expected_count}, Actual={count}, "
            f"Text='{search_str}', Case Sensitive={case_sensitive_flag}"
        )
        
        if count != expected_count:
            self._log("--- SCREEN DUMP (OCCURRENCE COUNT MISMATCH) ---")
            logger.console(result.stdout)
            raise AssertionError(
                f"Text '{search_str}' occurrence count mismatch in rows {start_row}-{end_row}.\n"
                f"Expected: {expected_count}\n"
                f"Actual:   {count}"
            )

    def verify_all_values_on_same_line(self, values):
        """Verifies that all comma-separated values appear on the same line.

        Takes a comma-separated string of values and verifies that all values
        appear together on at least one line of the screen.

        Args:
            values (str): Comma-separated values to search for (e.g., "ETHLIN02,ACTIVE").

        Returns:
            None

        Raises:
            AssertionError: If no line contains all the specified values.
            subprocess.CalledProcessError: If tmux capture-pane fails.

        Examples:
            Verify All Values On Same Line    ${WRKCFGSTS}
            Verify All Values On Same Line    ETHLIN02,ACTIVE
        """
        # Split the comma-separated values
        value_list = [v.strip() for v in str(values).split(',')]
        
        # Capture current screen content
        result = subprocess.run([
            "tmux", "capture-pane", "-p", "-t", self.session_name
        ], capture_output=True, text=True, check=True)
        
        # Check each line to see if it contains all values
        lines = result.stdout.splitlines()
        found_line = None
        
        for line_num, line in enumerate(lines, start=1):
            if all(value in line for value in value_list):
                found_line = line_num
                break
        
        self._log(
            f"Verifying all values on same line: {value_list}"
        )
        
        if found_line:
            self._log(f"All values found together on line {found_line}")
        else:
            self._log("--- SCREEN DUMP (VALUES NOT ON SAME LINE) ---")
            logger.console(result.stdout)
            raise AssertionError(
                f"Could not find all values on the same line: {value_list}"
            )

    def verify_numeric_value_greater_than(self, row, start_col, end_col, minimum_value):
        """Verifies that a numeric value at a position is greater than a minimum.

        Extracts text from the screen at specified coordinates, converts it to an
        integer, and verifies it's greater than the minimum value.

        Args:
            row (int or str): The row number (1-based) where the value appears.
            start_col (int or str): The starting column number (1-based).
            end_col (int or str): The ending column number (1-based).
            minimum_value (int or str): The minimum value (exclusive).

        Returns:
            None

        Raises:
            AssertionError: If the value is not greater than the minimum.
            ValueError: If the extracted text cannot be converted to an integer.
            subprocess.CalledProcessError: If tmux capture-pane fails.

        Examples:
            Verify Numeric Value Greater Than    3    68    71    ${DSPLIB}
            Verify Numeric Value Greater Than    5    10    15    1000
        """
        # Convert parameters
        row = int(row)
        start_col = int(start_col)
        end_col = int(end_col)
        minimum_value = int(minimum_value)
        
        # Capture current screen content
        result = subprocess.run([
            "tmux", "capture-pane", "-p", "-t", self.session_name
        ], capture_output=True, text=True, check=True)
        
        # Split into lines
        lines = result.stdout.splitlines()
        
        # Validate row number
        if row < 1 or row > len(lines):
            raise AssertionError(f"Row {row} out of range (screen has {len(lines)} lines)")
        
        # Extract the line and text at position
        line = lines[row - 1]
        actual_text = line[start_col - 1:end_col].strip()
        
        # Convert to integer
        try:
            actual_value = int(actual_text)
        except ValueError:
            self._log("--- SCREEN DUMP (NON-NUMERIC VALUE) ---")
            logger.console(result.stdout)
            raise ValueError(
                f"Text at position (row={row}, cols={start_col}-{end_col}) is not numeric.\n"
                f"Actual text: '{actual_text}'"
            )
        
        self._log(
            f"Numeric comparison: Row {row}, Cols {start_col}-{end_col}: "
            f"Actual={actual_value}, Minimum={minimum_value}"
        )
        
        if actual_value <= minimum_value:
            self._log("--- SCREEN DUMP (VALUE NOT GREATER THAN MINIMUM) ---")
            logger.console(result.stdout)
            raise AssertionError(
                f"Value at position (row={row}, cols={start_col}-{end_col}) is not greater than {minimum_value}.\n"
                f"Actual value: {actual_value}"
            )