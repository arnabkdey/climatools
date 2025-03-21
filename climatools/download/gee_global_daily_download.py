def download_ee_to_drive(
    start_date, 
    end_date, 
    collection_name="ECMWF/ERA5/DAILY", 
    band_name="minimum_2m_air_temperature",
    folder_name="EE_exports",
    file_prefix="data",
    region=None,
    scale=None,
    convert_kelvin=False,
    project_name=None
):
    """
    Exports Earth Engine data to Google Drive with flexible parameters.
    
    Parameters:
    -----------
    start_date : str
        Start date in format 'YYYY-MM-DD'
    end_date : str
        End date in format 'YYYY-MM-DD'
    collection_name : str
        Name of the Earth Engine image collection (default: "ECMWF/ERA5/DAILY")
    band_name : str
        Name of the band to export (default: "minimum_2m_air_temperature")
    folder_name : str
        Name of the folder in Google Drive where files will be saved
    file_prefix : str
        Prefix for exported filenames
    region : ee.Geometry, optional
        Region of interest. If None, uses global bounds
    scale : int, optional
        Resolution in meters. If None, uses native resolution
    convert_kelvin : bool
        Whether to convert from Kelvin to Celsius (for temperature data)
    project_name : str, optional
        Google Cloud project name for Earth Engine initialization
    """
    # Initialize Earth Engine with project if specified
    if project_name:
        ee.Initialize(project=project_name)
    else:
        ee.Initialize()
    
    # Convert dates
    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
    end_dt = datetime.strptime(end_date, '%Y-%m-%d')
    
    # Get date list
    date_list = []
    current_date = start_dt
    while current_date <= end_dt:
        date_list.append(current_date.strftime('%Y-%m-%d'))
        current_date += timedelta(days=1)
    
    # If no region is specified, use global bounds
    if region is None:
        region = ee.Geometry.Rectangle([-180, -90, 180, 90])
    
    # Get collection
    collection = ee.ImageCollection(collection_name)
    
    # Print available dates to debug
    first_date = ee.Date(collection.first().get('system:time_start')).format('YYYY-MM-dd').getInfo()
    last_date = ee.Date(collection.sort('system:time_start', False).first().get('system:time_start')).format('YYYY-MM-dd').getInfo()
    print(f"Collection {collection_name} available from {first_date} to {last_date}")
    
    for date in date_list:
        print(f"Processing date: {date}")
        
        try:
            # Create date objects for filtering
            start_date_ee = ee.Date(date)
            end_date_ee = start_date_ee.advance(1, 'day')
            
            # Filter and get image
            image = collection.filterDate(start_date_ee, end_date_ee).select(band_name).first()
            
            # Check if image exists
            image_info = image.getInfo()
            if image_info is None:
                print(f"No data available for {date}, skipping...")
                continue
            
            # If temperature data and conversion requested, convert from Kelvin to Celsius
            output_band_name = band_name
            if convert_kelvin:
                image = image.subtract(273.15)
                output_band_name = f"{band_name}_celsius"
                image = image.rename(output_band_name)
            
            # Export to Drive
            safe_date = date.replace("-", "")
            export_filename = f"{file_prefix}_{safe_date}"
            
            task = ee.batch.Export.image.toDrive(
                image=image,
                description=export_filename,
                folder=folder_name,
                region=region,
                scale=scale,
                crs='EPSG:4326',
                maxPixels=1e9,
                fileFormat='GeoTIFF'
            )
            
            task.start()
            print(f"Started export task for {date} to folder '{folder_name}' as '{export_filename}'")
            
            # Pause briefly to avoid hitting API limits
            time.sleep(1)
            
        except Exception as e:
            print(f"Error processing {date}: {str(e)}")
    
    print(f"All export tasks started. Check your Google Drive folder '{folder_name}'.")

if __name__ == "__main__":
    # Define parameters
    START_DATE = '2011-01-28'
    END_DATE = '2011-12-31'
    
    # Example 1: Default ERA5 minimum temperature with project specified
    download_ee_to_drive(
        start_date=START_DATE,
        end_date=END_DATE,
        folder_name="tmin_2011",
        file_prefix="tmin",
        convert_kelvin=True,
        project_name="your-project-id"  # Replace with your actual GCP project ID
    )
    
    # Example 2: With custom region (Continental US)
    us_region = ee.Geometry.Rectangle([-125, 24, -66, 50])
    download_ee_to_drive(
        start_date=START_DATE,
        end_date=END_DATE,
        collection_name="ECMWF/ERA5/DAILY",
        band_name="maximum_2m_air_temperature",
        folder_name="ERA5_max_temp_US",
        file_prefix="era5_max_temp_us",
        region=us_region,
        convert_kelvin=True,
        project_name="your-project-id"  # Replace with your actual GCP project ID
    )
    
    # Example 3: Different dataset - MODIS Land Surface Temperature
    download_ee_to_drive(
        start_date=START_DATE,
        end_date=END_DATE,
        collection_name="MODIS/006/MOD11A1",
        band_name="LST_Day_1km",
        folder_name="MODIS_LST",
        file_prefix="modis_lst",
        scale=1000,  # 1km resolution
        convert_kelvin=False,  # MODIS LST is in Kelvin but needs *0.02 not -273.15
        project_name="your-project-id"  # Replace with your actual GCP project ID
    )