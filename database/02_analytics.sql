/*
NEU Learning Hub - 02_analytics.sql
Microsoft SQL Server / T-SQL
Prerequisite: run 01_core.sql first.
Existing dbo.Students.StudentID is INT and is the FK target.
*/

USE [NEU_Learning_Hub];
GO

IF OBJECT_ID(N'dbo.StudentCourses', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.StudentCourses (
        StudentCourseID INT IDENTITY(1,1) NOT NULL CONSTRAINT PK_StudentCourses PRIMARY KEY,
        StudentID INT NOT NULL,
        CourseID INT NOT NULL,
        SemesterID INT NOT NULL,
        AttemptNumber TINYINT NOT NULL CONSTRAINT DF_StudentCourses_Attempt DEFAULT (1),
        CreditsSnapshot DECIMAL(5,2) NOT NULL,
        CountsTowardGPA BIT NOT NULL CONSTRAINT DF_StudentCourses_CountsGPA DEFAULT (1),
        CountsTowardCredits BIT NOT NULL CONSTRAINT DF_StudentCourses_CountsCredits DEFAULT (1),
        AttendanceScore DECIMAL(4,2) NULL,
        MidtermScore DECIMAL(4,2) NULL,
        FinalScore DECIMAL(4,2) NULL,
        CourseStatus NVARCHAR(20) NOT NULL CONSTRAINT DF_StudentCourses_Status DEFAULT (N'enrolled'),
        Note NVARCHAR(1000) NULL,
        CreatedAt DATETIME2(7) NOT NULL CONSTRAINT DF_StudentCourses_CreatedAt DEFAULT (SYSDATETIME()),
        UpdatedAt DATETIME2(7) NOT NULL CONSTRAINT DF_StudentCourses_UpdatedAt DEFAULT (SYSDATETIME()),
        CONSTRAINT FK_StudentCourses_Students FOREIGN KEY (StudentID) REFERENCES dbo.Students(StudentID),
        CONSTRAINT FK_StudentCourses_Courses FOREIGN KEY (CourseID) REFERENCES dbo.Courses(CourseID),
        CONSTRAINT FK_StudentCourses_Semesters FOREIGN KEY (SemesterID) REFERENCES dbo.Semesters(SemesterID),
        CONSTRAINT UQ_StudentCourses_Attempt UNIQUE (StudentID, CourseID, AttemptNumber),
        CONSTRAINT CK_StudentCourses_Attempt CHECK (AttemptNumber >= 1),
        CONSTRAINT CK_StudentCourses_Credits CHECK (CreditsSnapshot > 0),
        CONSTRAINT CK_StudentCourses_Attendance CHECK (AttendanceScore IS NULL OR AttendanceScore BETWEEN 0 AND 10),
        CONSTRAINT CK_StudentCourses_Midterm CHECK (MidtermScore IS NULL OR MidtermScore BETWEEN 0 AND 10),
        CONSTRAINT CK_StudentCourses_Final CHECK (FinalScore IS NULL OR FinalScore BETWEEN 0 AND 10),
        CONSTRAINT CK_StudentCourses_Status CHECK (CourseStatus IN (N'enrolled', N'completed', N'withdrawn', N'incomplete'))
    );
    CREATE INDEX IX_StudentCourses_Student_Semester
        ON dbo.StudentCourses(StudentID, SemesterID);
    CREATE INDEX IX_StudentCourses_Student_Status
        ON dbo.StudentCourses(StudentID, CourseStatus);
END;
GO

IF OBJECT_ID(N'dbo.AcademicGoals', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.AcademicGoals (
        GoalID INT IDENTITY(1,1) NOT NULL CONSTRAINT PK_AcademicGoals PRIMARY KEY,
        StudentID INT NOT NULL,
        GoalType NVARCHAR(20) NOT NULL,
        SemesterID INT NULL,
        TargetGPA DECIMAL(3,2) NOT NULL,
        CreatedAt DATETIME2(7) NOT NULL CONSTRAINT DF_AcademicGoals_CreatedAt DEFAULT (SYSDATETIME()),
        UpdatedAt DATETIME2(7) NOT NULL CONSTRAINT DF_AcademicGoals_UpdatedAt DEFAULT (SYSDATETIME()),
        CONSTRAINT FK_AcademicGoals_Students FOREIGN KEY (StudentID) REFERENCES dbo.Students(StudentID),
        CONSTRAINT FK_AcademicGoals_Semesters FOREIGN KEY (SemesterID) REFERENCES dbo.Semesters(SemesterID),
        CONSTRAINT CK_AcademicGoals_Type CHECK (
            (GoalType = N'semester' AND SemesterID IS NOT NULL) OR
            (GoalType = N'graduation' AND SemesterID IS NULL)
        ),
        CONSTRAINT CK_AcademicGoals_Target CHECK (TargetGPA BETWEEN 0 AND 4)
    );
    CREATE UNIQUE INDEX UX_AcademicGoals_Semester
        ON dbo.AcademicGoals(StudentID, SemesterID)
        WHERE GoalType = N'semester';
    CREATE UNIQUE INDEX UX_AcademicGoals_Graduation
        ON dbo.AcademicGoals(StudentID)
        WHERE GoalType = N'graduation';
END;
GO

IF OBJECT_ID(N'dbo.LearningActivities', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.LearningActivities (
        ActivityID INT IDENTITY(1,1) NOT NULL CONSTRAINT PK_LearningActivities PRIMARY KEY,
        StudentID INT NOT NULL,
        StudentCourseID INT NULL,
        Title NVARCHAR(200) NOT NULL,
        Description NVARCHAR(2000) NULL,
        ActivityType NVARCHAR(30) NOT NULL CONSTRAINT DF_LearningActivities_Type DEFAULT (N'other'),
        DueAt DATETIME2(7) NULL,
        CompletedAt DATETIME2(7) NULL,
        ActivityStatus NVARCHAR(20) NOT NULL CONSTRAINT DF_LearningActivities_Status DEFAULT (N'planned'),
        CreatedAt DATETIME2(7) NOT NULL CONSTRAINT DF_LearningActivities_CreatedAt DEFAULT (SYSDATETIME()),
        UpdatedAt DATETIME2(7) NOT NULL CONSTRAINT DF_LearningActivities_UpdatedAt DEFAULT (SYSDATETIME()),
        CONSTRAINT FK_LearningActivities_Students FOREIGN KEY (StudentID) REFERENCES dbo.Students(StudentID),
        CONSTRAINT FK_LearningActivities_StudentCourses FOREIGN KEY (StudentCourseID) REFERENCES dbo.StudentCourses(StudentCourseID),
        CONSTRAINT CK_LearningActivities_Type CHECK (ActivityType IN (N'assignment', N'study', N'exam_prep', N'project', N'other')),
        CONSTRAINT CK_LearningActivities_Status CHECK (ActivityStatus IN (N'planned', N'in_progress', N'completed', N'cancelled')),
        CONSTRAINT CK_LearningActivities_Completed CHECK (ActivityStatus <> N'completed' OR CompletedAt IS NOT NULL)
    );
    CREATE INDEX IX_LearningActivities_Student_Due
        ON dbo.LearningActivities(StudentID, DueAt);
    CREATE INDEX IX_LearningActivities_Student_Status
        ON dbo.LearningActivities(StudentID, ActivityStatus);
END;
GO

IF OBJECT_ID(N'dbo.AcademicAlerts', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.AcademicAlerts (
        AlertID INT IDENTITY(1,1) NOT NULL CONSTRAINT PK_AcademicAlerts PRIMARY KEY,
        StudentID INT NOT NULL,
        SemesterID INT NULL,
        StudentCourseID INT NULL,
        AlertTitle NVARCHAR(200) NOT NULL,
        AlertDescription NVARCHAR(2000) NOT NULL,
        Severity NVARCHAR(20) NOT NULL CONSTRAINT DF_AcademicAlerts_Severity DEFAULT (N'low'),
        AlertStatus NVARCHAR(20) NOT NULL CONSTRAINT DF_AcademicAlerts_Status DEFAULT (N'unread'),
        CreatedAt DATETIME2(7) NOT NULL CONSTRAINT DF_AcademicAlerts_CreatedAt DEFAULT (SYSDATETIME()),
        ReadAt DATETIME2(7) NULL,
        ResolvedAt DATETIME2(7) NULL,
        CONSTRAINT FK_AcademicAlerts_Students FOREIGN KEY (StudentID) REFERENCES dbo.Students(StudentID),
        CONSTRAINT FK_AcademicAlerts_Semesters FOREIGN KEY (SemesterID) REFERENCES dbo.Semesters(SemesterID),
        CONSTRAINT FK_AcademicAlerts_StudentCourses FOREIGN KEY (StudentCourseID) REFERENCES dbo.StudentCourses(StudentCourseID),
        CONSTRAINT CK_AcademicAlerts_Severity CHECK (Severity IN (N'high', N'medium', N'low')),
        CONSTRAINT CK_AcademicAlerts_Status CHECK (AlertStatus IN (N'unread', N'read', N'resolved'))
    );
    CREATE INDEX IX_AcademicAlerts_Student_Status
        ON dbo.AcademicAlerts(StudentID, AlertStatus, CreatedAt DESC);
END;
GO

/*
GPA rules for the Flask service layer:
- Course total = AttendanceScore * 0.10 + MidtermScore * 0.40 + FinalScore * 0.50.
- GPA = arithmetic average of recognized course grade points (not credit-weighted).
- For a retake, use the second-attempt score and cap the recognized 10-point score at 7.0.
- Convert recognized score to 4-point grade points using the project's grading.py mapping.
- Graduation credits are calculated separately using CreditsSnapshot and curriculum rules.
- Do not store a precomputed GPA in these tables; calculate it from completed course records.
- A semester goal has GoalType='semester' and SemesterID set.
- A graduation goal has GoalType='graduation' and SemesterID=NULL.
*/

PRINT N'02_analytics.sql: Analytics tables are ready.';
GO
