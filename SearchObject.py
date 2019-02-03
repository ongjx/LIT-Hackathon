from Search import Search
from bs4 import BeautifulSoup
import re
import os 
import json
import numpy as np
import scipy.stats as st

'''INITIALIZE OBJECT TO SEARCH COURT OF APPEAL'''

searchObject = Search('r1c1sc3')
search_terms = ['abuse', 'accidents', 'divorce', 'claims', 'tort']

''' REQUESTER '''
def makeRequest(search_terms):
    search_outputs = []
    documentsUrl = {}
    for term in search_terms:
        x = searchObject.make_search(term)
        soup = BeautifulSoup(x,'lxml')
        search_outputs.append(x)
        for i in soup.findAll('documentid'):
            if term not in documentsUrl:
                documentsUrl[term] = [i.getText()]
            else:
                documentsUrl[term] += [i.getText()]
    return documentsUrl

''' Get all requested urls '''
def getAllUrls():
    if os.path.isfile("urlCacheData.txt") == False:
        results = makeRequest(search_terms)
        return results
    return json.load(open('urlCacheData.txt'))

if os.path.isfile('urlCacheData.txt') == False:
    results = getAllUrls()
    json.dump(results, open('urlCacheData.txt','w'))
    getAllDocumentCode(results)
    
''' Get urls of a specific search term '''
def getUrlOfTerm(searchTerm):
    results = json.load(open('urlCacheData.txt'))
    return results[searchTerm]

''' MAKING REQUEST TO GET ALL THE DOCUMENT XML CODE '''
def getAllDocumentCode(doc_urls):

    if os.path.isfile('cacheSouceCodeData.txt') == False:
        documentsUrl = doc_urls
        src_codes = []
        for key, value in documentsUrl.items():
            for url in value:
                src_codes.append(searchObject.get_document(url))

        results = src_codes
        json.dump(results, open('cacheSouceCodeData.txt','w'))

    src_codes = json.load(open('cacheSouceCodeData.txt'))
    return src_codes

''' MAKING REQUEST TO GET DOCUMENT XML CODE OF A SPECIFIED TOPIC '''
def getTermDocumentCode(term, url_list):

    if os.path.isfile('cacheSouceCodeData_'+term+'.txt') == False:
        source_codes = []
        for url in url_list:
            source_codes.append(searchObject.get_document(url))

        results = source_codes
        json.dump(results, open('cacheSouceCodeData_'+term+'.txt','w'))  

    source_codes = json.load(open('cacheSouceCodeData_'+term+'.txt'))
    return source_codes

''' Checking appeal cases successful or failure rate'''
def getSuccessRate():
    src_codes = getAllDocumentCode(getAllUrls())
    appeal_success = 0
    appeal_failure = 0
    for source in src_codes:
        curr_success = 0
        curr_failure = 0
        soup = BeautifulSoup(source,'lxml')
        for p in soup.findAll('p'):
            p = str(p).lower()
            if 'appeal' in p:
                if 'allow' in p and 'dismiss' not in p:
                    curr_success += 1
                elif 'allow' not in p and 'dismiss' in p:
                    curr_failure += 1
        if curr_success > curr_failure:
            appeal_success += 1
        else:
            appeal_failure += 1
        
    print("Success: {} \tFailure: {}".format(appeal_success, appeal_failure))
    print("Turnover Rate: {}".format(appeal_success/(appeal_failure+appeal_success)))
    return appeal_success/(appeal_failure+appeal_success)
    # return appeal_success, appeal_failure

''' Finding who won and who lost '''
def appealVsRespond(src_codes):
    counsels_dict = {}
    for source in src_codes:
        soup = BeautifulSoup(source,'lxml')
        for counsel in soup.findAll('counsel'):
            output = counsel.getText()
            if 'respondent' in output:
                if 'r' not in counsels_dict:
                    counsels_dict['r'] = [output]
                else:
                    counsels_dict['r'] += [output]
            else:
                if 'a' not in counsels_dict:
                    counsels_dict['a'] = [output]
                else:
                    counsels_dict['a'] += [output]
    return counsels_dict

''' Some cleaning here, returns a cleaned dictionary '''
def cleaner(counsels_dict):
    counsels_dict_new = {}
    for k,v in counsels_dict.items():
        for item in v:
            item = re.sub(r'\([^)]*\)', '', item)
            item = re.sub('the appellant in person', '', item)
            item = re.sub('for appellants', '', item)
            item = re.sub('for appellant', '', item)
            item = re.sub('for the appellants', '', item)
            item = re.sub('for the appellant', '', item)
            item = re.sub('the appellant in person', '', item)
            item = re.sub('appellant', '', item)
            item = re.sub('Appellant in person', '', item)
            item = re.sub('for the applicants', '', item)
            item = re.sub('for the applicant', '', item)
            item = re.sub('for the respondents','', item)
            item = re.sub('for the respondent', '', item)
            item = re.sub('the respondent', '', item)
            item = re.sub('respondent', '', item)
            item = re.sub('for the first respondent', '', item)
            item = re.sub('for the beneficiaries','',item)
            item = re.sub('for the beneficiary','',item)
            item = re.sub('for the insurers','',item)
            item = re.sub('for the insurer','',item)
            item = re.sub('the Appellant in person', '', item)
            item = re.sub('for Appellants', '', item)
            item = re.sub('for Appellant', '', item)
            item = re.sub('for the Appellants', '', item)
            item = re.sub('for the Appellant', '', item)
            item = re.sub('the Appellant in person', '', item)
            item = re.sub('appellant', '', item)
            item = re.sub('for the Applicants', '', item)
            item = re.sub('for the Applicant', '', item)
            item = re.sub('for the Respondents','', item)
            item = re.sub('for the Respondent', '', item)
            item = re.sub('the Respondent', '', item)
            item = re.sub('respondent', '', item)
            item = re.sub('for the first Respondent', '', item)
            item = re.sub('for the beneficiaries','',item)
            item = re.sub('for the beneficiary','',item)
            item = re.sub('for the insurers','',item)
            item = re.sub('for the insurer','',item)
            item = re.sub('for the insureds','',item)
            item = re.sub(' for the','',item)
            item = re.sub('\xa0',' ',item)
            item = re.sub('[0-9/]', '', item)
            item = ''.join(item.split('\n')).strip()
            if k not in counsels_dict_new:
                counsels_dict_new[k] = [item]
            else:
                counsels_dict_new[k] += [item]

    new_counsel_dict = {}
    for k,v in counsels_dict_new.items():
        for i in v:
            temp_string = ''
            i = i.split()
            for j in i:
                temp_string += ''.join(j.strip()) + ' '
            if temp_string != '':
                if k not in new_counsel_dict:
                    new_counsel_dict[k] = [temp_string.strip()]
                else:
                    new_counsel_dict[k] += [temp_string.strip()]

    ''' EVEN MORE CLEANING '''
    for k,v in new_counsel_dict.items():
        for i in range(len(v)):
            v[i] = re.sub(',',' and',v[i])
            v[i] = re.sub('[.;]', '', v[i])
            v[i] = re.sub(' in Civil Appeal No of and in Civil Appeal No of', '', v[i])
            v[i] = re.sub(' in Civil Appeal No of and the in Civil Appeal No of ', '', v[i])
            v[i] = re.sub('in Civil Appeal No of and the s in Civil Appeal No of', '', v[i])
            v[i] = re.sub(' in Civil Appeal No of and the first in Civil Appeal No of', '', v[i])
            v[i] = re.sub(' s in Civil Appeal No of ', '', v[i])
            v[i] = re.sub(' in CA and s in CA', '', v[i])
            v[i] = re.sub(' in CA and in CA', '', v[i])
            v[i] = re.sub(' in CCA of in CCA of', '', v[i])
            v[i] = re.sub(' for the first', '', v[i])
            v[i] = re.sub(' for the second', '', v[i])
            v[i] = re.sub(' for the third', '', v[i])
            v[i] = re.sub(' for the fourth', '', v[i])
            v[i] = re.sub(' for the fifth', '', v[i])
            v[i] = re.sub(' for the sixth', '', v[i])
            v[i] = re.sub('and The third in person', '', v[i])
            v[i] = re.sub(' and second and fourth and fifth', '', v[i])
            v[i] = re.sub(' for in CA and in CA', '', v[i])
            v[i] = re.sub(' to fifth s', '', v[i])
            v[i] = re.sub(' to second s', '', v[i])
            v[i] = re.sub(' to sixth s', '', v[i])
            v[i] = re.sub(' and second s', '', v[i])
            v[i] = re.sub(' and sixth s', '', v[i])
            v[i] = re.sub(' and fifth s', '', v[i])
            v[i] = re.sub(' in Civil Appeal No of and the in Civil Appeal No of', '', v[i])
            v[i] = re.sub(' in Civil Appeal No of and s in Civil Appeal No of', '', v[i])
            v[i] = re.sub('with ', '', v[i])
            v[i] = re.sub(' with ', '', v[i])
            v[i] = re.sub(' SC', '', v[i])

    counsels_dict = {}
    for k,v in new_counsel_dict.items():
        for i in range(len(v)):
            temp_list = []
            for j in v[i].split('and'):
                stripped = j.strip()
                temp_list.append(stripped)
        
            if k not in counsels_dict:
                counsels_dict[k] = temp_list
            else:
                counsels_dict[k] += temp_list

    ''' ABIT MORE CLEANING '''
    new_counsel_dict = {}
    for k,v in counsels_dict.items():
        for name in v:
            if name != 'o' and name.lower() != 'sc' and name.lower() != 'the in person' and name.lower() != 'an' and name != '':
                if k not in new_counsel_dict:
                    new_counsel_dict[k] = [name]
                else:
                    new_counsel_dict[k] += [name]

    return new_counsel_dict

''' add all the lawyers into their respective case position - either A or R '''
def getLawyersInRespectiveCase(new_counsel_dict):
    appeallant_lawyers_dict = {}
    respondent_lawyers_dict = {}

    for k,v in new_counsel_dict.items():
        if k == 'a':
            for name in v:
                if name not in appeallant_lawyers_dict:
                    appeallant_lawyers_dict[name] = 1
                else:
                    appeallant_lawyers_dict[name] += 1
        else:
            for name in v:
                if name not in respondent_lawyers_dict:
                    respondent_lawyers_dict[name] = 1
                else:
                    respondent_lawyers_dict[name] += 1
    
    return appeallant_lawyers_dict, respondent_lawyers_dict


def getLawyersInCategory(category_file,category):
    src_codes = json.load(open(category_file))
    counsels_dict = {}
    for source in src_codes:
        soup = BeautifulSoup(source,'lxml')
        for counsel in soup.findAll('counsel'):
            output = counsel.getText()
            if 'respondent' in output:
                if (category,'r') not in counsels_dict:
                    counsels_dict[(category,'r')] = [output]
                else:
                    counsels_dict[(category,'r')] += [output]
            else:
                if (category,'a') not in counsels_dict:
                    counsels_dict[(category,'a')] = [output]
                else:
                    counsels_dict[(category,'a')] += [output]
    return counsels_dict
accidents = getLawyersInCategory('cacheSouceCodeData_accidents.txt','accidents')
tort = getLawyersInCategory('cacheSouceCodeData_tort.txt','tort')
abuse = getLawyersInCategory('cacheSouceCodeData_abuse.txt','abuse')
claims = getLawyersInCategory('cacheSouceCodeData_claims.txt','claims')
divorce = getLawyersInCategory('cacheSouceCodeData_divorce.txt','divorce')
list_category_dicts = [accidents, tort, abuse, claims, divorce]

def createDataBase(list_of_categories_dictionary):
    list_category_dicts_new = {}
    for category in list_category_dicts:
        clean = cleaner(category)
        for k,v in clean.items():
            if k not in list_category_dicts_new:
                list_category_dicts_new[k] = v
            else:
                list_category_dicts_new[k] += v
    return list_category_dicts_new
dataBase = createDataBase(list_category_dicts)


def get_lawyer_appearance_dict(cat_lawyer_dict):
    lawyer_dict = {}
    for cat, lawyer_list in cat_lawyer_dict.items():
        print('Fetching from', cat)
        for lawyer in lawyer_list:
            if lawyer not in lawyer_dict:
                lawyer_dict[lawyer] = 1
            else:
                lawyer_dict[lawyer] += 1
        # print(f' Num of Unique Lawyers : {len(lawyer_dict)} '.center(50,'='))

    # for name, count in lawyer_dict.items():
    #     print(name + ':', count)
    print(f' Num of Unique Lawyers : {len(lawyer_dict)} '.center(50,'='))
    print(f' Total Num of cases : {sum(lawyer_dict.values())} '.center(50, '='))
    return lawyer_dict

lawyer_appearance_dict = get_lawyer_appearance_dict(createDataBase(list_category_dicts))


''' categories key dict references to my dataBase''' 
def getLawyerHistory(lawyer_Name):

    history = {}
    for key,value in dataBase.items(): #database
        for name in value:
            if lawyer_Name.lower() in name.lower():
                if key not in history:
                    history[key] = 1
                else:
                    history[key] += 1
    return history 

success_rate = getSuccessRate()

def getRecommendation(lawyerName):
    lawyerDetail = getLawyerHistory(lawyerName)
    lawyerName = lawyerName.title()
    count = lawyer_appearance_dict[lawyerName]
    reco_count = 0
    reco_count_total = 0
    for key,value in lawyerDetail.items():
        # print("this is the value", value)
        if key[1].lower() == 'r':
            reco_count += (1-success_rate)*value
            reco_count_total += value
        else:
            reco_count += success_rate*value
            reco_count_total += value
    # print('this is reco count', reco_count, 'this is reco total', reco_count_total)
    recommendation = reco_count/((reco_count_total)*0.75 + count * 0.25)
    return "{:.2f}".format(recommendation)

''' Calculate specific Lawyer's potential Salary '''
#   recommendation from getRecommendation
def getExpertise(lawyerName):
    history = getLawyerHistory(lawyerName)
    expertise_dict = {}
    side_dict = {}
    for tuple_key in history:
        values = history[tuple_key]
        if tuple_key[0] not in expertise_dict:
            expertise_dict[tuple_key[0]] = values
        else:
            expertise_dict[tuple_key[0]] += values
            
        if tuple_key[1] not in side_dict:
            side_dict[tuple_key[1]] = values
        else:
            side_dict[tuple_key[1]] += values
    max_expertise = 0
    max_expertise_count = 0
    max_side = 0
    max_side_count = 0
    
    for key in expertise_dict:
        value = expertise_dict[key]
        if value > max_expertise_count:
            max_expertise = key
            max_expertise_count = value
            
    for key in side_dict:
        value = side_dict[key]
        if value > max_side_count:
            max_side = key
            max_side_count = value

    if max_side == "R":
        max_side = "RESPONDENTS"
    else:
        max_side = "APPELLANTS"

    return max_expertise, max_side

def getSalary(lawyerName): 
    lawyerName = lawyerName.title()
    recommendation = float(getRecommendation(lawyerName))
    cases = lawyer_appearance_dict[lawyerName]
    low = 1000
    high = 5000

    experience = round(cases/5)

    while experience > 0:

        if experience < 2:
            low *= 1.042
            high *= 1.042
        else:
            low *= 1.077
            high *= 1.077

        experience -= 1

    if recommendation >= 0.65:
        low *= 1.1
        high *= 1.1
        
    elif recommendation >= 0.4:
        low *= 1.05
        high *= 1.05

    low = round(low)
    high = round(high)
    sal_range = range(low, high)

    sal_CI = st.norm.interval(0.95, loc=np.mean(sal_range), scale=1.96*np.mean(sal_range)**(1/2))
    sal_CI_round_2 = (round(sal_CI[0],2),round(sal_CI[1],2))
    
    return sal_CI_round_2