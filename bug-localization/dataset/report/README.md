/*********************************************************************************************************************************************************/
/**	This dataset was used to evaluate the learning-to-rank approach introduced in a paper draft that was submitted to FSE2014.                      **/
/**     This dataset contains bug reports, commit history, and API descriptions of six open source Java projects.                                       **/
/**     The six projects are AspectJ, Birt, Eclipse Platform UI, JDT, SWT, and Tomcat.                                                                  **/
/**     This README file also introduces commands that were used to check out different versions of the source code packages of these six projects.     **/
/**	Author: Xin Ye                                                                                                                                  **/
/**	email: xy348709@ohio.edu                                                                                                                        **/
/**	2014.03.04                                                                                                                                      **/
/*********************************************************************************************************************************************************/

File: 
	dataset_fse2014.sql	--	a mysqldump backup file that was created using MySQL 5.1.44

Import: 
	Step 1:	You need to install a MySQL database by yourself.
	Step 2: Restore all databases from the file above using the following command:
		mysql -u root -p < dataset_fse2014.sql

Database Summary:
	API_Descriptions	--	The database that contains API descriptions and all file names of every of the six projects.
	AspectJ			--	The database that contains bug reports and commit history of AspectJ.
	Birt			--	The database that contains bug reports and commit history of Birt.
	Eclipse_Platform_UI	--	The database that contains bug reports and commit history of Eclipse Platform UI.
	JDT			--	The database that contains bug reports and commit history of JDT.
	SWT			--	The database that contains bug reports and commit history of SWT.
	Tomcat			--	The database that contains bug reports and commit history of Tomcat.


Database:
	API_Descriptions
Table:	
	aspectj, birt, Eclipse, jdt, swt, tomcat	--	tables that contain API descriptions of classes and interfaces in six projects respectively
Columns:	
	"class_url" is the column that contains the url that links to each class/interface specification in the project API documents.
	"description" is the column that contains the corresponding API descriptions including all superclasses, implemented interfaces, 
	and superinterfaces descriptions of this class/interface.
Table:
	aspectj_files, birt_files, eclipse_files, jdt_files, swt_files, tomcat_files	--	tables that contain file names of six projects respectively 
Columns:
	"file_name" is the column that contains the full path of each of the files including those deleted files in the project revision history.
	"index_id" is the file id. We give each file in the project revision history a unique file id for evaluation purpose.


Database:
	AspectJ, Birt, Eclipse_Platform_UI, JDT, SWT, Tomcat
Table:
	bug_and_files	--	the table that contains bug report information and related commit information of mapped bug reports that were actually used in evaluation
Columns:
	"bug_id" is the bug report id
	"summary" is the bug report summary
	"description" is the bug report description
	"bag_of_word_stemmed" is the bag of words from both the summary and description after tokenization and stemming
	"summary_stemmed" is the bag of words from the summary after tokenization and stemming
	"description_stemmed" is the bag of words from the description after tokenization and stemming
	"report_time" is the bug report report time
	"report_timestamp" is the bug report report timestamp
	"status" is the status of the bug report
	"commit" is the SHA-1 hash id for the commit that fixed the bug report
	"commit_timestamp" is the commit timestamp
	"files" contains the full path of every Java file that was fixed in this commit 
	
Table:
	bug_commit	--	the table that contains bug report information and commit information of all bug reports that were mentioned in the git log messages
Columns:
	"bug_id" is the bug report id
	"summary" is the bug report summary
	"description" is the bug report description
	"report_time" is the bug report report time
	"reporter" is the author who reported this bug
	"assignee" is the assignee of this bug report
	"status" is the status of the bug report
	"product" is the related product
	"component" is the related component of the related product
	"importance" is the priority of this bug report 
	"commit" is the SHA-1 hash id for the commit that fixed the bug report
	"author" is the author who commit the fix
	"commit_time" is the commit time
	"log" is the commit log message
	"files" contains the full path of every Java file that was fixed in this commit 
Table:
	file_history	--	the table that contains the bug-fixing history information of every source file
Columns:
	"doc_id" is the unique file id we gave before
	"file_name" is the full path of each of the source files including those deleted files in the project revision history
	"bug_id" contains the bug report id of every previously fixed bug report for which this source file was fixed

/*************************************************************************************************************************************************/
Source Codes to check out:

AspectJ:
git clone git://git.eclipse.org/gitroot/aspectj/org.aspectj.git

Birt:
git clone https://git.eclipse.org/r/p/birt/org.eclipse.birt

Eclipse Platform UI:
git clone https://git.eclipse.org/r/p/platform/eclipse.platform.ui

JDT:
git clone https://git.eclipse.org/r/p/jdt/eclipse.jdt.ui

SWT:
git clone https://git.eclipse.org/r/p/platform/eclipse.platform.swt

Tomcat:
git clone git://git.apache.org/tomcat.git

Check out the before-fix version of the source code package:
To check out a before-fix version of the source code package for a bug report, see the following example.
Take Eclipse Bug 420972 for example, this bug was fixed at commit "657bd90". To check out the before-fix version "2143203" of the source code package, use the following command:
git checkout 657bd90~1

Index only the changed files: 
When evaluate bug 420972, we check out its before-fix version "2143203" and index all the source files. 
When evaluate another bug report 423588, we need to check out its before-fix version "602d549" of the source code package. But we do not need to index all the source files again.
We just index the changed files.
To obtain a list of "Added" Java files of version "602d549", compare with version "2143203", use the following commands:
git diff --name-status 2143203 602d549 | grep ".java$" | grep "^A"
To obtain a list of "Modified" Java files of version "602d549", compare with version "2143203", use the following commands:
git diff --name-status 2143203 602d549 | grep ".java$" | grep "^M"
To obtain a list of "Deleted" Java files of version "602d549", compare with version "2143203", use the following commands:
git diff --name-status 2143203 602d549 | grep ".java$" | grep "^D"

