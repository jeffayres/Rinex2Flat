from datetime import datetime

def parse_cn0_rinex(filepath, target_date):
    # Define the date format in the RINEX file
    rinex_date_format = "%Y-%m-%d"

    # Convert target date to datetime for comparison
    target_date = datetime.strptime(target_date, rinex_date_format)
    rinex_date = None
    rinex_type = None

    with open(filepath, 'r') as f:
        header_end = False
        cn0_indices = []
        obs_types = []
        cn0_data = []

        # Step 1: Parse Header for Date, Type, and Observation Types
        for line in f:
            if "END OF HEADER" in line:
                header_end = True
                break

            # Extract RINEX type and date information
            if "RINEX VERSION / TYPE" in line:
                rinex_type = line[20:40].strip()
            elif "PGM / RUN BY / DATE" in line:
                # Get the file creation date from the header
                rinex_date_str = line[40:].strip()
                rinex_date = rinex_date_str.split()[0]  # Take only the date portion

            # Parse observation type definitions for C/N0 values
            if "SYS / # / OBS TYPES" in line:
                parts = line.split()
                obs_types = parts[3:]  # Observation types list

                # Identify C/N0 indices and observation types in the list
                for i, obs in enumerate(obs_types):
                    if obs.startswith("C"):  # Common prefix for C/N0 types
                        cn0_indices.append((i, obs))  # Store index and obs type

        # Step 2: Parse Observation Data for the Specific Date
        current_epoch_data = None  # Initialize before looping through data lines

        for line in f:
            # New epoch line (starts with ">")
            if line.startswith(">"):
                # Reset current_epoch_data for each new epoch
                current_epoch_data = None

                # Parse the date and time from the epoch line
                year = int(line[2:6])
                month = int(line[7:9])
                day = int(line[10:12])
                hour = int(line[13:15])
                minute = int(line[16:18])
                second = float(line[19:29])
                epoch_date = datetime(year, month, day, hour, minute, int(second))

                # Format epoch as numeric-only timestamp
                epoch_str = epoch_date.strftime("%Y%m%d%H%M%S")

                # Check if the epoch matches the target date
                if epoch_date.date() == target_date.date():
                    # Set current_epoch_data if it’s the right date
                    current_epoch_data = epoch_str
            elif current_epoch_data is not None:
                # Parse satellite observation data line
                prn = line[:3].strip()  # Satellite PRN as a numeric value
                obs_values = line[3:].split()

                # Extract each C/N0 value and its signal type
                for i, obs_type in cn0_indices:
                    if i < len(obs_values):
                        cno_value = obs_values[i]
                        # Append numeric-only formatted data
                        cn0_data.append(f"{current_epoch_data},{prn},{obs_type[1:]},{cno_value}")

    # Step 3: Write the parsed C/N0 data for the specific date to a .txt file
    output_filename = f'{target_date.strftime("%Y%m%d")}_CN0_data_.txt'
    with open(output_filename, 'w') as output_file:
        # Write header lines with date, type, and column descriptions
        output_file.write(f"% RINEX Date: {rinex_date}, Type: {rinex_type}\n")
        output_file.write("% Epoch, PRN, Sig, CNO\n")
        
        # Write each row of numeric-only C/N0 data
        for entry in cn0_data:
            output_file.write(entry + "\n")

    print(f"C/N0 data parsing completed for {target_date.date()}. Data saved to {output_filename}.")

# Call the function with the provided RINEX file path and target date
parse_cn0_rinex('cat20010.16o', '2023-11-02')