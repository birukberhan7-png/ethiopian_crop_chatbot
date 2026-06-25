-- ============================================================
-- Ethiopian Crop Recommendation Chatbot - SQL Server Schema
-- Compatible with Microsoft SQL Server 2019+
-- ============================================================

USE master;
GO

IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'EthiopianCropDB')
  CREATE DATABASE EthiopianCropDB;
GO

USE EthiopianCropDB;
GO

-- ── Regions ────────────────────────────────────────────────────────────────
CREATE TABLE Regions (
  RegionID   INT IDENTITY(1,1) PRIMARY KEY,
  RegionName NVARCHAR(100) NOT NULL UNIQUE,
  AltitudeMin INT,
  AltitudeMax INT,
  Description NVARCHAR(500)
);

-- ── Crops ──────────────────────────────────────────────────────────────────
CREATE TABLE Crops (
  CropID         INT IDENTITY(1,1) PRIMARY KEY,
  CropName       NVARCHAR(100) NOT NULL UNIQUE,
  LocalName      NVARCHAR(100),       -- Amharic name
  Description    NVARCHAR(1000),
  AltitudeMin    INT,
  AltitudeMax    INT,
  TempMin        FLOAT,
  TempMax        FLOAT,
  RainfallMin    FLOAT,
  RainfallMax    FLOAT,
  PHMin          FLOAT,
  PHMax          FLOAT,
  HarvestDays    NVARCHAR(50),
  PlantingTips   NVARCHAR(1000),
  IsEndemic      BIT DEFAULT 1,
  CreatedAt      DATETIME2 DEFAULT GETDATE()
);

-- ── Users ──────────────────────────────────────────────────────────────────
CREATE TABLE Users (
  UserID       INT IDENTITY(1,1) PRIMARY KEY,
  Username     NVARCHAR(100) NOT NULL UNIQUE,
  Email        NVARCHAR(200) UNIQUE,
  RegionID     INT REFERENCES Regions(RegionID),
  FarmAltitude INT,
  CreatedAt    DATETIME2 DEFAULT GETDATE()
);

-- ── Recommendations (prediction log) ──────────────────────────────────────
CREATE TABLE Recommendations (
  RecID          INT IDENTITY(1,1) PRIMARY KEY,
  SessionID      NVARCHAR(100),
  UserID         INT REFERENCES Users(UserID),
  Temperature    FLOAT,
  Humidity       FLOAT,
  Rainfall       FLOAT,
  SoilPH         FLOAT,
  Altitude       FLOAT,
  SoilType       NVARCHAR(50),
  Nitrogen       FLOAT,
  Phosphorus     FLOAT,
  Potassium      FLOAT,
  RegionID       INT REFERENCES Regions(RegionID),
  RecommendedCrop NVARCHAR(100) REFERENCES Crops(CropName),
  Confidence     FLOAT,
  Source         NVARCHAR(50),   -- 'ml_model' | 'rule_based'
  CreatedAt      DATETIME2 DEFAULT GETDATE()
);

-- ── Chat Logs ──────────────────────────────────────────────────────────────
CREATE TABLE ChatLogs (
  LogID      INT IDENTITY(1,1) PRIMARY KEY,
  SessionID  NVARCHAR(100) NOT NULL,
  Role       NVARCHAR(10) NOT NULL CHECK(Role IN ('user','bot')),
  Message    NVARCHAR(MAX) NOT NULL,
  CreatedAt  DATETIME2 DEFAULT GETDATE()
);
GO

-- ── Seed: Regions ──────────────────────────────────────────────────────────
INSERT INTO Regions (RegionName, AltitudeMin, AltitudeMax, Description) VALUES
('Oromia',           500, 3200, 'Largest region; diverse agro-ecology from highland to lowland'),
('Amhara',          1200, 4200, 'Ethiopian highlands; major grain-producing region'),
('Tigray',          1000, 3000, 'Northern highland; drought-prone but fertile valleys'),
('Sidama',          1500, 2500, 'Coffee and Enset belt in southern Ethiopia'),
('SNNPR',            500, 4200, 'Diverse region; Enset, Coffee, and highland crops'),
('Afar',              20, 1500, 'Lowland arid zone; Sorghum and Millet dominant'),
('Somali',            80, 1500, 'Semi-arid lowland; drought-resistant crops'),
('Benishangul-Gumuz', 500, 2100, 'Lowland to mid-altitude; Maize and Sorghum');
GO

-- ── Seed: Crops ────────────────────────────────────────────────────────────
INSERT INTO Crops (CropName, LocalName, Description, AltitudeMin, AltitudeMax, TempMin, TempMax, RainfallMin, RainfallMax, PHMin, PHMax, HarvestDays, PlantingTips, IsEndemic) VALUES
('Teff',          'ጤፍ',     'Ethiopias iconic grain; basis of injera. Most important cereal crop.',                1500, 2800, 18, 25, 500,  900, 5.5, 7.0, '85-95 days',  'Plant at onset of main rains (June-July). Broadcast sow at 5 kg/ha.',   1),
('Enset',         'እንሰት',   'False Banana; fermented staple for millions in southern Ethiopia.',                   1500, 3000, 10, 25, 1000,1500, 5.5, 6.5, '5-10 years',  'Plant suckers in well-prepared pits. Perennial crop.',                  1),
('Coffee Arabica','ቡና',     'Birthplace of Arabica coffee; premium export crop.',                                  1500, 2200, 15, 24, 1200,2000, 5.5, 6.5, 'Oct-Feb',     'Shade-grown under forest trees. Plant seedlings in nursery first.',     1),
('Noug',          'ኑግ',     'Ancient Ethiopian oilseed (Guizotia abyssinica); used for edible oil.',              1500, 2500, 15, 25, 700, 1200, 5.5, 7.0, '90-120 days', 'Tolerates waterlogged black soils. Broadcast seed at 5-8 kg/ha.',      1),
('Barley',        'ገብስ',    'Oldest Ethiopian cereal; vital for tella and high-altitude food security.',           2000, 3500,  5, 20, 400,  700, 5.5, 7.5, '90-120 days', 'Plant in Meher season. Excellent cold tolerance.',                      0),
('Sorghum',       'ማሾ',    'Drought-tolerant lowland staple for semi-arid Ethiopia.',                              500, 1500, 25, 35, 400,  700, 5.5, 7.5, '90-130 days', 'Plant at start of rains. Highly drought-tolerant once established.',    0),
('Finger Millet', 'ዳጉሣ',   'Nutritious grain important for food security; high calcium and iron.',                1000, 2200, 18, 28, 500, 1000, 5.0, 7.0, '90-120 days', 'Excellent for inter-cropping. Tolerates poor soils.',                   1),
('Chickpea',      'ሽምብራ',  'Key legume crop and protein source; also fixes nitrogen in soil.',                    1500, 2500, 15, 25, 500,  900, 5.5, 7.0, '75-100 days', 'Excellent rotation crop. Inoculate seeds with Rhizobium.',             0),
('Linseed',       'ተልባ',   'Oilseed and fiber crop grown in Ethiopian highlands.',                                2000, 3000, 15, 22, 600, 1000, 5.5, 7.0, '90-120 days', 'Cool highland crop. Excellent for Meher season.',                      1),
('Maize',         'በቆሎ',   'Major food crop across Ethiopias mid-altitude zones.',                                1000, 2500, 18, 30, 700, 1200, 5.5, 7.0, '90-120 days', 'Plant at start of main rains. Space 75x25 cm. Weed at 2-4 weeks.',     0);
GO

PRINT 'Database schema and seed data created successfully.';
GO
