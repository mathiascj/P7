XML_FILE = 'temp.xml'
Q_FILE = 'temp.q'

def get_best_time(recipes, modules, template_file, verifyta):
    m_map, w_map, r_map =\
        generate_xml(template_file, modules,
			recipes, xml_name, q_name)
    
	result, trace = run_verifyta(
				XML_FILE, Q_FILE,
				"-t 2", "-o 3",
				"-u", "-y",
			    	verifyta=verifyta)


    time = trace_time(trace)
    trace_iter = iter((trace.decode('utf-8')).splitlines())
    worked_on, transported_through, active_works = \
	get_travsersal_info(trace_iter, m_map, r_map, w_map)
	
	return time, worked_on, transported_through, active_works

