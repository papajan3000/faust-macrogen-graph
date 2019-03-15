import re
from datetime import datetime, timedelta

def year_comparison(manuscript, existing_manuscript_source, source_name, special_researchers):
    """Checks if the year of an already existing manuscript source is greater or smaller than the year of a different source for the same 
        manuscript. The greater year will be returned. If the year doesn't appear inside the researchers name, the year of the special
        researchers dictionary will be taken (the dates are taken from the following website: http://faustedition.net/bibliography).
    
    Args:
        manuscript (string): String of the manuscript.
        existing_manuscript_source (string): Researcher of the manuscript already in a dictionary.
        source_name (string): Possible different researchers for the same manuscript.
        special_resarchers (dict): Dictionary with sources (string) as keys and their publication year (int) as values.     
    Returns:
        False if the year inside the existing_manuscript_source string is greater than the year in the source_name string.
    """
    greater = False

    existing_year = re.match(r".*([1-3][0-9]{3})", existing_manuscript_source)
    actual_year = re.match(r".*([1-3][0-9]{3})", source_name)
            
    if existing_year is not None and actual_year is not None:
        existing_year = int(existing_year.group(1))
        actual_year = int(actual_year.group(1))
        
        if existing_year > actual_year:
            greater = False
        elif actual_year >= existing_year:
            greater = True
        
    elif existing_year is None and actual_year is not None:
        if existing_manuscript_source in special_researchers:
            existing_year = special_researchers[existing_manuscript_source]
            actual_year = int(actual_year.group(1))
            
            if existing_year > actual_year:
                greater = False
            elif actual_year >= existing_year:
                greater = True
                
    elif existing_year is not None and actual_year is None:
        if source_name in special_researchers:
            existing_year = int(existing_year.group(1))
            actual_year = special_researchers[source_name]
            
            if existing_year > actual_year:
                greater = False
            elif actual_year >= existing_year:
                greater = True

    return greater
     

def dates_wissenbach(date_items, special_researchers):
    """Generates a dictionary following the approach of Wissenbach (see: resources/vitt_macrogen.pdf, p. 12) where the middle of two dates
        is concatenated with a manuscript instead of multiple dates.
        
        Args:
            date_items (list): List of tupels with the following structure: ([source], (manuscript), {notBefore: year, notAfter: year, when: year}).
            special_resarchers (dict): Dictionary with sources (string) as keys and their publication year (int) as values.     
        Returns:
            Dictionary with the manuscripts as keys and 2-tuples as values with the structure (middle of date, source).
    """
    
    wissenbach_dict = {}
    
    for item in date_items:
        source_name = item[0][0]
        manuscript = item[1][0]
        dates_dict = item[2]
        
        notbefore = dates_dict["notBefore"]
        notafter = dates_dict["notAfter"]
        when = dates_dict["when"]
        
        mid_date = "-"
        
        if when != "-":
            mid_date = datetime.strptime(when, '%Y-%m-%d')
        elif notafter == "-" and notbefore != "-":
            mid_date = datetime.strptime(notbefore, '%Y-%m-%d')
        elif notbefore == "-" and notafter != "-":
            mid_date = datetime.strptime(notafter, '%Y-%m-%d')
        elif notbefore != "-" and notafter != "-":
            nb_date = datetime.strptime(notbefore, '%Y-%m-%d')
            na_date = datetime.strptime(notafter, '%Y-%m-%d')

            mid_date = nb_date + (na_date - nb_date) / 2
        
        #not adding falsely tagged date-elements (6 elements exist)
        if mid_date != "-":
            if manuscript in wissenbach_dict:
                existing_manuscript_source = wissenbach_dict[manuscript][1]
                
                #if there is a conflict between two researchers who classify the manuscript date differently, the newer one will be taken
                greater = year_comparison(manuscript, existing_manuscript_source, source_name, special_researchers)
                
                if greater:
                    wissenbach_dict[manuscript] = (mid_date, source_name)
                else:
                    pass
            else:
                wissenbach_dict[manuscript] = (mid_date, source_name)
                
    return wissenbach_dict


def dates_vitt(date_items):
    """Generates a dictionary following the approach of Vitt (see: resources/vitt_macrogen.pdf, p. 13) where the manuscripts and the dates
        of the manuscripts are treated as nodes. If an exact date for a manuscript exists (@when), the manuscript gets a higher weight-value.
        
        Args:
            date_items (list): List of tupels with the following structure: ([source], (manuscript), {notBefore: year, notAfter: year, when: year}).
        Returns:
            Dictionary with the manuscripts as keys and 2-,3- or 4-tuples as values with the structure (start_date, source_name) or
            (start_date, source_name, 10.0) or (start_date, source_name, 1.0, end_date).
    """
    vitt_dict = {}
    
    for item in date_items:
        source_name = item[0][0]
        manuscript = item[1][0]
        dates_dict = item[2]
        
        notbefore = dates_dict["notBefore"]
        notafter = dates_dict["notAfter"]
        when = dates_dict["when"]
        
        start_date = "-"
        end_date = "-"
        
        if when != "-":
            start_date = datetime.strptime(when, '%Y-%m-%d')
            vitt_dict[manuscript] = (start_date, source_name, 10.0)
        elif notafter == "-" and notbefore != "-":
            start_date = datetime.strptime(notbefore, '%Y-%m-%d')
            vitt_dict[manuscript] = (start_date, source_name)
        elif notbefore == "-" and notafter != "-":
            start_date = datetime.strptime(notafter, '%Y-%m-%d')
            vitt_dict[manuscript] = (start_date, source_name)
        elif notbefore != "-" and notafter != "-":
            start_date = datetime.strptime(notbefore, '%Y-%m-%d')
            end_date = datetime.strptime(notafter, '%Y-%m-%d')
            vitt_dict[manuscript] = (start_date, source_name, 1.0, end_date)
    
    return vitt_dict


def dates_paulus(date_items, special_researchers, notbeforedate=True):
    """Generate a dictionary following one of two approaches of Paulus (author of this project) where the manuscripts and the dates
        of the manuscripts are treated as nodes but only one date is connected with manuscript (there is a choice between @notBefore
        or @notAfter dates). If an exact date for a manuscript exists (@when), the manuscript gets a higher weight-value.
        
        Args:
            date_items (list): List of tupels with the following structure: ([source], (manuscript), {notBefore: year, notAfter: year, when: year}).
            special_resarchers (dict): Dictionary with sources (string) as keys and their publication year (int) as values.
            notbeforedate (bool): If True, the manuscripts will be connected with the @notBefore-Date, else with the @notAfter-Date.
        Returns:
            Dictionary with the manuscripts as keys and 2- or 3-tuples as values with the structure (start_date, source_name) or
            (start_date, source_name, 10.0).
    """

    paulus_dict = {}
    
    for item in date_items:
        source_name = item[0][0]
        manuscript = item[1][0]
        dates_dict = item[2]
        
        notbefore = dates_dict["notBefore"]
        notafter = dates_dict["notAfter"]
        when = dates_dict["when"]
        
        start_date = "-"
        
        if notbeforedate:
            if notbefore != "-":    
                start_date = datetime.strptime(notbefore, '%Y-%m-%d')
            elif when != "-":
                start_date = datetime.strptime(when, '%Y-%m-%d')
            #if notBefore and when were not provieded with a date, notAfter will be taken instead
            elif notafter != "-" and notbefore == "-":
                start_date = datetime.strptime(notafter, '%Y-%m-%d')
        else:
            if notafter != "-":
                start_date = datetime.strptime(notafter, '%Y-%m-%d')
            elif when != "-":
                start_date = datetime.strptime(when, '%Y-%m-%d')
            #if notAfter and when were not provieded with a date, notBefore will be taken instead
            elif notbefore != "-" and notafter == "-":
                start_date = datetime.strptime(notbefore, '%Y-%m-%d')
        
        #not adding falsely tagged date-elements (6 elements exist)
        if start_date != "-":
            #if there is a conflict between two researchers who classify the manuscript date differently, the newer one will be taken
            if manuscript in paulus_dict:
                existing_manuscript_source = paulus_dict[manuscript][1]
                greater = year_comparison(manuscript, existing_manuscript_source, source_name, special_researchers)
                
                if greater:
                    if when != "-":
                        paulus_dict[manuscript] = (start_date, source_name, 10.0)
                    else:
                        paulus_dict[manuscript] = (start_date, source_name)
                else:
                    pass
            else:
                if when != "-":
                    paulus_dict[manuscript] = (start_date, source_name, 10.0)
                else:
                    paulus_dict[manuscript] = (start_date, source_name)
            
    return paulus_dict


def dates_shorter_period(date_items, factor):
    """Generates a dictionary similiar to the Vitt-approach where the manuscripts and the dates
        of the manuscripts are treated as nodes and an exact manuscript date gets a higher weight. 
        Differently than the Vitt-approach, the "notBefore"- and "notAfter"-dates will be changed 
        based on a factor, so that the period between the two dates will shrink. 
    
    Args:
        date_items (list): List of tupels with the following structure: ([source], (manuscript), {notBefore: year, notAfter: year, when: year}).
        factor (int): Integer which will be divided with the period between two dates or added/subtracted from a date.
    Returns:
        Dictionary with the manuscripts as keys and 2-,3- or 4-tuples as values with the structure (start_date, source_name) or
        (start_date, source_name, 10.0) or (start_date, source_name, 1.0, end_date).
    """
    
    sp_dict = {}
    
    for item in date_items:
        source_name = item[0][0]
        manuscript = item[1][0]
        dates_dict = item[2]
        
        notbefore = dates_dict["notBefore"]
        notafter = dates_dict["notAfter"]
        when = dates_dict["when"]
        
        start_date = "-"
        end_date = "-"
        
        if when != "-":
            start_date = datetime.strptime(when, '%Y-%m-%d')
            sp_dict[manuscript] = (start_date, source_name, 10.0)
        elif notafter == "-" and notbefore != "-":
            start_date = datetime.strptime(notbefore, '%Y-%m-%d')
            sp_dict[manuscript] = (start_date, source_name)
        elif notbefore == "-" and notafter != "-":
            start_date = datetime.strptime(notafter, '%Y-%m-%d')
            sp_dict[manuscript] = (start_date, source_name)
        elif notbefore != "-" and notafter != "-":
            start_date = datetime.strptime(notbefore, '%Y-%m-%d')
            end_date = datetime.strptime(notafter, '%Y-%m-%d')
            
            period = end_date - start_date
            period = period.days
        
            x = 0
            
            if period < factor:
                x = 0
            else:
                x = int(period/factor)
                
            start_date = start_date + timedelta(days=x)
            end_date = end_date - timedelta(days=x)
            
            sp_dict[manuscript] = (start_date, source_name, 1.0, end_date)
    
    return sp_dict


def dates_longer_period(date_items, factor):
    """Generates a dictionary similiar to the Vitt-approach where the manuscripts and the dates
        of the manuscripts are treated as nodes and an exact manuscript date gets a higher weight. 
        Differently than the Vitt-approach, the "notBefore"- and "notAfter"-dates will be changed 
        based on a factor, so that the period between the two dates will increase. 
    
    Args:
        date_items (list): List of tupels with the following structure: ([source], (manuscript), {notBefore: year, notAfter: year, when: year}).
        factor (int): Integer which will be divided with the period between two dates or added/subtracted from a date.
    Returns:
        Dictionary with the manuscripts as keys and 2-,3- or 4-tuples as values with the structure (start_date, source_name) or
        (start_date, source_name, 10.0) or (start_date, source_name, 1.0, end_date).
    """
    
    lp_dict = {}
    
    for item in date_items:
        source_name = item[0][0]
        manuscript = item[1][0]
        dates_dict = item[2]
        
        notbefore = dates_dict["notBefore"]
        notafter = dates_dict["notAfter"]
        when = dates_dict["when"]
        
        start_date = "-"
        end_date = "-"
        
        if when != "-":
            start_date = datetime.strptime(when, '%Y-%m-%d')
            lp_dict[manuscript] = (start_date, source_name, 10.0)
        elif notafter == "-" and notbefore != "-":
            start_date = datetime.strptime(notbefore, '%Y-%m-%d')
            lp_dict[manuscript] = (start_date, source_name)
        elif notbefore == "-" and notafter != "-":
            start_date = datetime.strptime(notafter, '%Y-%m-%d')
            lp_dict[manuscript] = (start_date, source_name)
        elif notbefore != "-" and notafter != "-":
            start_date = datetime.strptime(notbefore, '%Y-%m-%d')
            end_date = datetime.strptime(notafter, '%Y-%m-%d')
            
            start_date = start_date - timedelta(days=factor)
            end_date = end_date + timedelta(days=factor)
            
            lp_dict[manuscript] = (start_date, source_name, 1.0, end_date)
    
    return lp_dict
   
