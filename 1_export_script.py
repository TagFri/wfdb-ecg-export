#Import dependencies and tools
import csv
import random
import matplotlib.pyplot as plt
import wfdb

#Variables to adjust number of total ECG
numberOfNormal = 40
numberOfEachSCP = 4
#Status output to terminal
print("\033[1mDatabase export started!\033[0;0m")

#--------------------------
### IMPORT DATABASE INFORMATION FROM CSV
#--------------------------
file = open("02ptblxl_dataset.csv", "r")
data = list(csv.reader(file, delimiter = "," ))
fullDatabase = [row for row in data]
file.close()
#Status output to terminal
print("-> Database csv read")

#Convert database rows to correct data types and strip to only necessary info:
cleanDatabase = []
for fullEcgData in fullDatabase[1:]:
    #Convert gender from 0/1 to male/female
    fullEcgData[3] = 'female' if fullEcgData[3] == "1" else "male"
    # 0 -> 0 = ECG ID
    # 1 -> 1 = Patient ID
    # 2 -> 2 = Age
    # 3 -> 3 = Sex
    # 11 -> 4  = SCP code
    # 18 -> 5 = verified by humans
    cleanDatabase.append([int(fullEcgData[0]), float(fullEcgData[1]), int(float(fullEcgData[2])), fullEcgData[3], fullEcgData[11], fullEcgData[18]])
#Check that cleansed database maintains it's length
assert len(cleanDatabase) == 21799

#--------------------------
### CLEAN DATABASE BY EXCLUSION/INCLUSION CRITERIAS
#--------------------------
patientIncluded = []
limitedDatabase = []
for ecgData in cleanDatabase:
    # Select only ECG that are verified by humans, over age 16 and patient not already included
    if (ecgData[1] not in patientIncluded) and (ecgData[2] > 16) and (ecgData[2] != 300.0) and (ecgData[5] == "True"):
        #Add patient to included patients to avoid future for duplicates:
        patientIncluded.append(ecgData[1])
        #Append only list of ecgID, SCP-codes, age and sex
        limitedDatabase.append([ecgData[0],ecgData[4], ecgData[2], ecgData[3]])
#Check that length after inclusion criteria is 14130 (checked with excel)
assert len(limitedDatabase) == 14130
#Status output to terminal
print(f"-> All ECG not verified by humans, <16yo and duplicate patients removed ({len(cleanDatabase) - len(limitedDatabase)})")

#--------------------------
### SELECT ECG FROM CLEANED DATABASE
#--------------------------

### SELECT PATHOLOGICAL ECG'S
patologicalECG = []
#SCP categories as given on ptb-xl webpage:
scpPathologyCategories = ["STACH","SVTAC","SBRAD","AFIB","AFLT","SVARR","PSVT","WPW","SARRH","LPR","1AVB","2AVB","3AVB","CLBBB","ILBBB","CRBBB","IRBBB","IVCD","LAFB","LPFB","PRC(S)","BIGU","AMI","ALMI","ASMI","INJAS","INJAL","INJLA","ILMI","IMI","IPLMI","IPMI","INJIN","INJIL","LMI","PMI","ISC_","ISCAL","ISCAS","ISCLA","ISCAN","ISCIN","ISCIL","NST_","STE_","STD_","NDT","NT_","LOWT","INVT","TAB_","VCLVH","LVH","RVH","LVOLT","HVOLT","LAO/LAE","RAO/RAE","SEHYP","LNGQT","ABQRS","PVC","QWAVE","PAC","TRIGU","DIG","EL","ANEUR"]
#Shuffle SCP list randomly, avoid bias of always starting with the same
random.shuffle(scpPathologyCategories)
#Choosen 6 ECG per SCP
for scp in scpPathologyCategories:
    #append ecgID for hver ecgRecord i selected Database som har valgt scp i seg:
    allEcgWithScp = [[ecgRec[0],ecgRec[2],ecgRec[3]]  for ecgRec in limitedDatabase if scp in ecgRec[1]]
    #Randomize all ecg within one SCP
    random.shuffle(allEcgWithScp)
    #Keep 6 of each scp:
    allEcgWithScp = allEcgWithScp[:numberOfEachSCP]
    for ecg in allEcgWithScp:
        patologicalECG.append(ecg)
#Check that total number of ecg match wanted outcome.
assert len(patologicalECG) == len(scpPathologyCategories) * numberOfEachSCP
#Status output to terminal
print(f'-> Each SCP has been shuffled and {numberOfEachSCP} ecg of each been chosen')

### SELECT NORMAL ECG'S
normalECG = []
scpNormalCategories = ["Norm", "SR"]
for ecgRec in limitedDatabase:
    if "NORM" in ecgRec[1] and "SR" in ecgRec[1]:
        normalECG.append([ecgRec[0],ecgRec[2],ecgRec[3]])
random.shuffle(normalECG)
normalECG = normalECG[:numberOfNormal]
assert len(normalECG) == numberOfNormal
#Status output to terminal
print(f'-> Normal ECG has been shuffled and 100 ecg chosen')

#--------------------------
### DELETE DUPLICATE ECG'S
#--------------------------
print(f'-> Deleting duplicate ecgs...')
allEcg = patologicalECG + normalECG
uniqeEcg = []
for ecg in allEcg:
    if ecg in uniqeEcg:
        print(f"          excluded ecg {str(ecg)}")
    else:
        uniqeEcg.append(ecg)
assert(len(allEcg) >= len(uniqeEcg))
random.shuffle(uniqeEcg)
#Status output to terminal
print(f'-> {len(allEcg)-len(uniqeEcg)} duplicate ECG has been deleted')
print(f'THE TOTAL NUMBER OF ECGS ARE {len(uniqeEcg)}')

#--------------------------
### EXPORT CSV WITH ORIGINAL ECG ID VS NEW ID
#--------------------------
f = open('04original_ecg_id.csv', 'w')
writer = csv.writer(f)
i = 1
for id in uniqeEcg:
    write = [str(i),str(id)]
    writer.writerow(write)
    i+=1
f.close()
#INFORMATION OUTPUT
print(f'-> CSV with original vs. new number has been exported')

#--------------------------
### EXPORT LIST OF GENDER/AGE TO USE IN CHECKLIST
#--------------------------
f = open('04ageAndGender.csv', 'w')
writer = csv.writer(f)
i = 1
for id in uniqeEcg:
    write = [int(id[1]), str(id[2])]
    writer.writerow(write)
    i+=1
f.close()
#INFORMATION OUTPUT
print(f'-> CSV with age/gender has been exported')

#--------------------------
### GRAFICAL REPRESENTATION
#--------------------------

#Import pyplot and wfdb to import database and visualize
#Need to have installed the depencencies INSIDE the same folder as this script
print(f'-> \033[1mStarting ECG plotting:\033[0;0m')
#export list of ecg records from textfile:
num = 1
# For loop to go through records form 0 to x in a choicen databaase:
for id in uniqeEcg:
    # choose recordName to look for in databse
    if int(id[0]) < 10:
        recordName = '0000' + str(int(id[0])) + '_lr'
    elif int(id[0]) < 100:
        recordName = '000' + str(int(id[0])) + '_lr'
    elif int(id[0]) < 1000:
        recordName = '00' + str(int(id[0])) + '_lr'
    elif int(id[0]) < 10000:
        recordName = '0' + str(int(id[0])) + '_lr'
    else:
        recordName = str(int(id[0])) + '_lr'

    # Choose filepath in databse to look for recordName
    if int(id[0]) < 1000:
        filepath = '00000' + '/'
    elif int(id[0]) < 10000:
        filepath = '0' + recordName[1:2] + '000/'
    else:
        filepath = recordName[0:2] + "000/"

    ecgRecord = wfdb.rdrecord(recordName, pn_dir='ptb-xl/records100/' + filepath)

    #naming the file for blinding
    ecgName = 'Case Number ' + str(num) + ' - ' + str(id[2]) + ' ' + str(id[1]) + " years old"

    #Visulice ECG to figure with our paramters GAMMEL

    ecgFigure = wfdb.plot_wfdb(
        record=ecgRecord,       #CSV fil som er lest inn over i wfdb
        title=ecgName,           #Tittel pp enkel fil?
        time_units = 'seconds', #x-akse tidsakse
        plot_sym = False,        # Plotter symboler på graf for referanse
        ecg_grids='all',        #12 avl som visualiseres,  0.5mV, and minor grids at 0.125mV som default
        ann_style=["I", "II","III","aVR","aVL","aVF","V1","V2","V3","V4","V5","V6"],
        figsize=(39,100),       #Proposjoner og oppløsning på bilde
        sig_style = [[2.5,-2]], #Gir +2.5 -> -2 på y-akses på alle avledningene
        sharex = True,          #Liner alle grafer ift. x-aksen
        return_fig=True)        #Lagre bilde

    #Save figure to local location
    path = '/05_ecgs/' + ecgName
    plt.savefig(path + '.pdf', format="pdf", bbox_inches="tight")
    #Clear figure to avoid memory overload
    plt.clf()
    plt.close('all')
    # INFORMATION OUTPUT
    print(f"ECG number {num} has been exported")
    num +=1

#Status output to terminal
print('\033[1mScript sucessfull\033[0;0m')