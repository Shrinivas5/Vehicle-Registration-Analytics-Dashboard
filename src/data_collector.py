import requests
import pandas as pd
import json
from datetime import datetime, timedelta
import time
import logging
from typing import Dict, List, Optional

class VahanDataCollector:
    """
    Data collector for Vahan Dashboard vehicle registration data
    Specifically targets: https://vahan.parivahan.gov.in/vahan4dashboard/vahan/view/reportview.xhtml
    As specified in the assignment requirements
    """
    
    def __init__(self):
        self.base_url = "https://vahan.parivahan.gov.in/vahan4dashboard"
        self.report_endpoint = "/vahan/view/reportview.xhtml"  # Exact URL from assignment
        self.full_api_url = f"{self.base_url}{self.report_endpoint}"
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/html, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://vahan.parivahan.gov.in/'
        })
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Log the target URL for clarity
        self.logger.info(f"VahanDataCollector initialized for: {self.full_api_url}")
    
    def get_vehicle_data(self, start_date: str, end_date: str, state_code: str = "DL") -> Dict:
        """
        Fetch vehicle registration data from Vahan Dashboard
        URL: https://vahan.parivahan.gov.in/vahan4dashboard/vahan/view/reportview.xhtml
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            state_code: State code (default: DL for Delhi)
        
        Returns:
            Dictionary containing vehicle registration data
        """
        try:
            # Updated payload based on actual Vahan Dashboard parameters
            payload = {
                'startDate': start_date,
                'endDate': end_date,
                'stateCode': state_code,
                'reportType': 'vehicle_category',
                'format': 'json',
                'vehicleType': 'ALL'  # Add vehicle type parameter
            }
            
            self.logger.info(f"Fetching data from Vahan Dashboard: {self.full_api_url}")
            self.logger.info(f"Parameters: {payload}")
            
            # Try different HTTP methods and headers
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'application/json, text/html, */*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': 'https://vahan.parivahan.gov.in/',
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-Requested-With': 'XMLHttpRequest'
            }
            
            # First try POST request
            response = self.session.post(self.full_api_url, data=payload, headers=headers, timeout=30)
            
            # If POST fails, try GET request
            if response.status_code != 200:
                self.logger.info("POST request failed, trying GET request...")
                response = self.session.get(self.full_api_url, params=payload, headers=headers, timeout=30)
            
            response.raise_for_status()
            
            # Better response handling - check content type and handle different formats
            content_type = response.headers.get('content-type', '')
            
            if 'application/json' in content_type:
                try:
                    data = response.json()
                    if data:
                        self.logger.info(f"Successfully fetched JSON data for {start_date} to {end_date}")
                        return data
                    else:
                        self.logger.warning("API returned empty JSON response")
                        return {}
                except json.JSONDecodeError as json_err:
                    self.logger.error(f"JSON parsing error: {json_err}")
                    self.logger.debug(f"Response content: {response.text[:200]}...")
                    return {}
            elif 'text/html' in content_type:
                # Handle HTML responses (common with government portals)
                self.logger.info("API returned HTML response, attempting to extract data")
                extracted_data = self.extract_data_from_html(response.text)
                if extracted_data:
                    return extracted_data
                else:
                    self.logger.warning("Could not extract data from HTML response")
                    return {}
            else:
                self.logger.warning(f"Unexpected content type: {content_type}")
                self.logger.debug(f"Response content: {response.text[:200]}...")
                return {}
            
        except requests.RequestException as e:
            self.logger.error(f"Error fetching data from {self.full_api_url}: {e}")
            self.logger.warning("Falling back to sample data generation for development")
            return {}
        except Exception as e:
            self.logger.error(f"Unexpected error during data fetch: {e}")
            return {}
    
    def get_manufacturer_data(self, start_date: str, end_date: str, vehicle_type: str = "2W") -> Dict:
        """
        Fetch manufacturer-wise registration data from Vahan Dashboard
        URL: https://vahan.parivahan.gov.in/vahan4dashboard/vahan/view/reportview.xhtml
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            vehicle_type: Vehicle type (2W, 3W, 4W)
        
        Returns:
            Dictionary containing manufacturer-wise data
        """
        try:
            payload = {
                'startDate': start_date,
                'endDate': end_date,
                'vehicleType': vehicle_type,
                'reportType': 'manufacturer',
                'format': 'json'
            }
            
            self.logger.info(f"Fetching manufacturer data from: {self.full_api_url}")
            
            response = self.session.post(self.full_api_url, data=payload, timeout=30)
            response.raise_for_status()
            
            # Better response handling - check content type and handle different formats
            content_type = response.headers.get('content-type', '')
            
            if 'application/json' in content_type:
                try:
                    data = response.json()
                    if data:
                        self.logger.info(f"Successfully fetched manufacturer data for {vehicle_type}")
                        return data
                    else:
                        self.logger.warning("API returned empty JSON response for manufacturer data")
                        return {}
                except json.JSONDecodeError as json_err:
                    self.logger.error(f"JSON parsing error for manufacturer data: {json_err}")
                    self.logger.debug(f"Response content: {response.text[:200]}...")
                    return {}
            elif 'text/html' in content_type:
                self.logger.info("API returned HTML response for manufacturer data")
                extracted_data = self.extract_data_from_html(response.text)
                if extracted_data:
                    return extracted_data
                else:
                    self.logger.warning("Could not extract manufacturer data from HTML response")
                    return {}
            else:
                self.logger.warning(f"Unexpected content type for manufacturer data: {content_type}")
                return {}
            
        except requests.RequestException as e:
            self.logger.error(f"Error fetching manufacturer data from {self.full_api_url}: {e}")
            self.logger.warning("Falling back to sample data generation for development")
            return {}
        except Exception as e:
            self.logger.error(f"Unexpected error during manufacturer data fetch: {e}")
            return {}

    def test_vahan_connection(self) -> bool:
        """
        Test connection to the Vahan Dashboard endpoint
        Returns True if connection is successful, False otherwise
        """
        try:
            test_response = self.session.get(self.base_url, timeout=10)
            if test_response.status_code == 200:
                self.logger.info("✅ Successfully connected to Vahan Dashboard")
                return True
            else:
                self.logger.warning(f"⚠️ Vahan Dashboard returned status code: {test_response.status_code}")
                return False
        except requests.RequestException as e:
            self.logger.error(f"❌ Failed to connect to Vahan Dashboard: {e}")
            return False
    
    def generate_sample_data(self) -> pd.DataFrame:
        """
        Generate sample vehicle registration data for development/testing
        This simulates real Vahan Dashboard data structure
        """
        import random
        from datetime import datetime, timedelta
        from dateutil.relativedelta import relativedelta  # Added proper date handling
        
        # Generate data for last 4+ years, quarterly, up to current date
        start_date = datetime(2021, 1, 1)
        end_date = datetime.now()  # Use current date instead of fixed 2024-12-31
        
        data = []
        manufacturers_2w = ['Hero MotoCorp', 'Honda', 'TVS', 'Bajaj', 'Yamaha', 'Royal Enfield']
        manufacturers_4w = ['Maruti Suzuki', 'Hyundai', 'Tata Motors', 'Mahindra', 'Kia', 'Toyota']
        manufacturers_3w = ['Bajaj Auto', 'TVS', 'Mahindra', 'Piaggio', 'Atul Auto']
        
        current_date = start_date
        while current_date <= end_date:
            quarter = f"Q{((current_date.month - 1) // 3) + 1}"
            year = current_date.year
            month = current_date.month  # Add month extraction
            
            # 2-Wheeler data
            for manufacturer in manufacturers_2w:
                base_registrations = random.randint(50000, 200000)
                growth_factor = random.uniform(0.8, 1.3)  # -20% to +30% growth
                registrations = int(base_registrations * growth_factor)
                
                data.append({
                    'date': current_date.strftime('%Y-%m-%d'),
                    'year': year,
                    'quarter': quarter,
                    'month': month,  # Add month column
                    'vehicle_type': '2W',
                    'manufacturer': manufacturer,
                    'registrations': registrations
                })
            
            # 4-Wheeler data
            for manufacturer in manufacturers_4w:
                base_registrations = random.randint(20000, 80000)
                growth_factor = random.uniform(0.85, 1.25)
                registrations = int(base_registrations * growth_factor)
                
                data.append({
                    'date': current_date.strftime('%Y-%m-%d'),
                    'year': year,
                    'quarter': quarter,
                    'month': month,  # Add month column
                    'vehicle_type': '4W',
                    'manufacturer': manufacturer,
                    'registrations': registrations
                })
            
            # 3-Wheeler data
            for manufacturer in manufacturers_3w:
                base_registrations = random.randint(5000, 25000)
                growth_factor = random.uniform(0.9, 1.2)
                registrations = int(base_registrations * growth_factor)
                
                data.append({
                    'date': current_date.strftime('%Y-%m-%d'),
                    'year': year,
                    'quarter': quarter,
                    'month': month,  # Add month column
                    'vehicle_type': '3W',
                    'manufacturer': manufacturer,
                    'registrations': registrations
                })
            
            current_date = current_date + relativedelta(months=3)
        
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])
        
        self.logger.info(f"Generated sample data with {len(df)} records from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        return df
    
    def save_data(self, df: pd.DataFrame, filename: str = "vehicle_data.csv"):
        """Save data to CSV file"""
        df.to_csv(f"data/{filename}", index=False)
        self.logger.info(f"Data saved to data/{filename}")

    def collect_all_data_up_to_today(self, start_date: str = '2021-01-01') -> pd.DataFrame:
        """
        Collect comprehensive vehicle registration data up to today from Vahan Dashboard.
        Fetches for all vehicle types and combines vehicle category and manufacturer data.
        """
        from datetime import datetime
        
        end_date = datetime.now().strftime('%Y-%m-%d')
        self.logger.info(f"Collecting data from {start_date} to {end_date} (today)")
        
        vehicle_types = ['2W', '3W', '4W']
        all_data = []

        for v_type in vehicle_types:
            self.logger.info(f"Fetching data for {v_type} vehicles...")
            
            # Fetch vehicle data
            vehicle_data = self.get_vehicle_data(start_date, end_date, state_code='ALL')
            # Fetch manufacturer data for this type
            manufacturer_data = self.get_manufacturer_data(start_date, end_date, v_type)

            # Process and combine data
            if vehicle_data and 'records' in vehicle_data:
                df_vehicle = pd.DataFrame(vehicle_data['records'])
                df_vehicle['vehicle_type'] = v_type
                all_data.append(df_vehicle)
                self.logger.info(f"Added {len(df_vehicle)} {v_type} vehicle records")
            elif vehicle_data:
                # Handle different data structure
                df_vehicle = pd.DataFrame(vehicle_data)
                df_vehicle['vehicle_type'] = v_type
                all_data.append(df_vehicle)
                self.logger.info(f"Added {len(df_vehicle)} {v_type} vehicle records (alternative format)")
            
            if manufacturer_data and 'records' in manufacturer_data:
                df_manuf = pd.DataFrame(manufacturer_data['records'])
                df_manuf['vehicle_type'] = v_type
                all_data.append(df_manuf)
                self.logger.info(f"Added {len(df_manuf)} {v_type} manufacturer records")
            elif manufacturer_data:
                # Handle different data structure
                df_manuf = pd.DataFrame(manufacturer_data)
                df_manuf['vehicle_type'] = v_type
                all_data.append(df_manuf)
                self.logger.info(f"Added {len(df_manuf)} {v_type} manufacturer records (alternative format)")

            time.sleep(1)  # Rate limiting

        if all_data:
            combined_df = pd.concat(all_data, ignore_index=True)
            # Add derived columns
            combined_df['date'] = pd.to_datetime(combined_df.get('date', end_date))
            combined_df['year'] = combined_df['date'].dt.year
            combined_df['quarter'] = 'Q' + combined_df['date'].dt.quarter.astype(str)
            combined_df['month'] = combined_df['date'].dt.month
            
            self.logger.info(f"Successfully collected {len(combined_df)} total records from Vahan Dashboard")
            return combined_df
        else:
            self.logger.warning("No data collected from Vahan Dashboard, falling back to sample data")
            return pd.DataFrame()

    def extract_data_from_html(self, html_content: str) -> Dict:
        """
        Extract vehicle registration data from HTML response
        This handles cases where the Vahan Dashboard returns HTML instead of JSON
        
        Args:
            html_content: HTML content from the response
            
        Returns:
            Dictionary with extracted data or empty dict if extraction fails
        """
        try:
            from bs4 import BeautifulSoup
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Look for data tables in the HTML
            tables = soup.find_all('table')
            data = {}
            
            # Also look for data in divs or other elements that might contain registration info
            potential_data_elements = soup.find_all(['div', 'span', 'p'], class_=lambda x: x and any(keyword in x.lower() for keyword in ['data', 'registration', 'vehicle', 'count']))
            
            for table in tables:
                # Try to find vehicle registration data
                rows = table.find_all('tr')
                if len(rows) > 1:  # At least header + data
                    headers = [th.get_text(strip=True) for th in rows[0].find_all(['th', 'td'])]
                    
                    # Check if this looks like vehicle data
                    if any('vehicle' in header.lower() or 'registration' in header.lower() or 'count' in header.lower()
                           for header in headers):
                        table_data = []
                        for row in rows[1:]:  # Skip header
                            cells = row.find_all(['td', 'th'])
                            row_data = [cell.get_text(strip=True) for cell in cells]
                            if len(row_data) == len(headers):
                                table_data.append(dict(zip(headers, row_data)))
                        
                        if table_data:
                            data['vehicle_registrations'] = table_data
                            self.logger.info(f"Extracted {len(table_data)} records from HTML table")
                            break
            
            # If no table data found, try to extract from other elements
            if not data and potential_data_elements:
                self.logger.info("Attempting to extract data from alternative HTML elements...")
                # Look for patterns like "Total: X" or "Registrations: Y"
                text_content = soup.get_text()
                
                # Try to find registration numbers in text
                import re
                registration_patterns = [
                    r'(\d{1,3}(?:,\d{3})*)\s*(?:registrations?|vehicles?)',
                    r'total[:\s]+(\d{1,3}(?:,\d{3})*)',
                    r'count[:\s]+(\d{1,3}(?:,\d{3})*)'
                ]
                
                for pattern in registration_patterns:
                    matches = re.findall(pattern, text_content, re.IGNORECASE)
                    if matches:
                        self.logger.info(f"Found potential registration data: {matches}")
                        # Create a basic structure
                        data['extracted_counts'] = [int(match.replace(',', '')) for match in matches]
                        break
            
            if not data:
                self.logger.warning("No data could be extracted from HTML response")
                self.logger.debug(f"HTML content preview: {html_content[:500]}...")
            
            return data
            
        except Exception as e:
            self.logger.error(f"Error extracting data from HTML: {e}")
            return {}