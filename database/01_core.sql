/*
NEU Learning Hub - 01_core.sql
Microsoft SQL Server / T-SQL
Run against database: NEU_Learning_Hub

Existing tables Students, StudentAccounts, AdminAccounts are NOT recreated.
This script creates shared academic reference tables only.
*/

USE [NEU_Learning_Hub];
GO

IF OBJECT_ID(N'dbo.AcademicPrograms', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.AcademicPrograms (
        ProgramID INT IDENTITY(1,1) NOT NULL CONSTRAINT PK_AcademicPrograms PRIMARY KEY,
        ProgramCode NVARCHAR(40) NOT NULL,
        ProgramName NVARCHAR(200) NOT NULL,
        TotalCredits DECIMAL(6,2) NULL,
        Description NVARCHAR(1000) NULL,
        IsActive BIT NOT NULL CONSTRAINT DF_AcademicPrograms_IsActive DEFAULT (1),
        CreatedAt DATETIME2(7) NOT NULL CONSTRAINT DF_AcademicPrograms_CreatedAt DEFAULT (SYSDATETIME()),
        CONSTRAINT UQ_AcademicPrograms_ProgramCode UNIQUE (ProgramCode),
        CONSTRAINT CK_AcademicPrograms_TotalCredits CHECK (TotalCredits IS NULL OR TotalCredits > 0)
    );
END;
GO

IF OBJECT_ID(N'dbo.Courses', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.Courses (
        CourseID INT IDENTITY(1,1) NOT NULL CONSTRAINT PK_Courses PRIMARY KEY,
        CourseCode NVARCHAR(40) NOT NULL,
        CourseName NVARCHAR(200) NOT NULL,
        Description NVARCHAR(1000) NULL,
        CreatedAt DATETIME2(7) NOT NULL CONSTRAINT DF_Courses_CreatedAt DEFAULT (SYSDATETIME()),
        CONSTRAINT UQ_Courses_CourseCode UNIQUE (CourseCode)
    );
END;
GO

IF OBJECT_ID(N'dbo.Semesters', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.Semesters (
        SemesterID INT IDENTITY(1,1) NOT NULL CONSTRAINT PK_Semesters PRIMARY KEY,
        AcademicYear NVARCHAR(20) NOT NULL,
        TermNumber TINYINT NOT NULL,
        SemesterName NVARCHAR(100) NOT NULL,
        StartDate DATE NULL,
        EndDate DATE NULL,
        SemesterStatus NVARCHAR(20) NOT NULL CONSTRAINT DF_Semesters_Status DEFAULT (N'upcoming'),
        CreatedAt DATETIME2(7) NOT NULL CONSTRAINT DF_Semesters_CreatedAt DEFAULT (SYSDATETIME()),
        CONSTRAINT UQ_Semesters_Year_Term UNIQUE (AcademicYear, TermNumber),
        CONSTRAINT CK_Semesters_TermNumber CHECK (TermNumber BETWEEN 1 AND 3),
        CONSTRAINT CK_Semesters_Dates CHECK (StartDate IS NULL OR EndDate IS NULL OR StartDate <= EndDate),
        CONSTRAINT CK_Semesters_Status CHECK (SemesterStatus IN (N'upcoming', N'current', N'completed'))
    );
END;
GO

IF OBJECT_ID(N'dbo.CurriculumCourses', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.CurriculumCourses (
        CurriculumCourseID INT IDENTITY(1,1) NOT NULL CONSTRAINT PK_CurriculumCourses PRIMARY KEY,
        ProgramID INT NOT NULL,
        CourseID INT NOT NULL,
        Credits DECIMAL(5,2) NOT NULL,
        RequirementType NVARCHAR(20) NOT NULL CONSTRAINT DF_CurriculumCourses_Requirement DEFAULT (N'required'),
        SuggestedSemester TINYINT NULL,
        CountsTowardGPA BIT NOT NULL CONSTRAINT DF_CurriculumCourses_GPA DEFAULT (1),
        CountsTowardGraduationCredits BIT NOT NULL CONSTRAINT DF_CurriculumCourses_GradCredits DEFAULT (1),
        DisplayOrder INT NOT NULL CONSTRAINT DF_CurriculumCourses_DisplayOrder DEFAULT (0),
        CONSTRAINT UQ_CurriculumCourses_Program_Course UNIQUE (ProgramID, CourseID),
        CONSTRAINT FK_CurriculumCourses_Programs FOREIGN KEY (ProgramID)
            REFERENCES dbo.AcademicPrograms(ProgramID),
        CONSTRAINT FK_CurriculumCourses_Courses FOREIGN KEY (CourseID)
            REFERENCES dbo.Courses(CourseID),
        CONSTRAINT CK_CurriculumCourses_Credits CHECK (Credits > 0),
        CONSTRAINT CK_CurriculumCourses_Requirement CHECK (RequirementType IN (N'required', N'elective')),
        CONSTRAINT CK_CurriculumCourses_SuggestedSemester CHECK (SuggestedSemester IS NULL OR SuggestedSemester BETWEEN 1 AND 12)
    );
END;
GO

PRINT N'01_core.sql: Shared academic tables are ready.';
GO
