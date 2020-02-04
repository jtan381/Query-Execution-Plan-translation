import copy
import json
import queue
import re

import psycopg2
from JsonToText import PlanToText


class Communicator:
    hostname = 'None'
    dbName = 'None'
    username = 'None'
    password = 'None'
    port = 'None'

    qep1_plan = None
    qep2_plan = None

    def __init__ (self):
        self.con = None
        self.cur = None
        self.qep1 = None
        self.qep2 = None


    def ReInit_DB (self):
        if (self.con):
            #disconnect first
            self.cur.close()
            self.con.close()
            #reconnect
            try:
                self.con = psycopg2.connect(
                    host=self.hostName,
                    database=self.dbName,
                    user=self.username,
                    password=self.password,
                    port=self.portNo
                )
                self.cur = self.con.cursor()
                return
            except (Exception, psycopg2.Error) as error:
                self.CloseConnection()
                return
        return

    def init_DB (self, dbName, username, password, hostName, portNo):
        messages = ""
        self.hostName = hostName
        self.dbName = dbName
        self.username = username
        self.password = password
        self.portNo = portNo
        try:
            self.con = psycopg2.connect(
                host=self.hostName,
                database=self.dbName,
                user=self.username,
                password=self.password,
                port=self.portNo
            )
            self.cur = self.con.cursor()
            return True, self.getTableList(), self.GetAttrDict()

        except (Exception, psycopg2.Error) as error:
            self.CloseConnection()
            return False, [], {}


    def GetAttrDict (self):
        sql = """SELECT table_name,column_name
        FROM information_schema.columns
        WHERE table_schema IN (select schema_name
        from information_schema.schemata WHERE schema_name NOT IN('pg_toast','pg_temp_1','pg_toast_temp_1','pg_catalog','information_schema')) 
        ORDER BY table_name;"""
        self.cur.execute(sql)
        rows = self.cur.fetchall()
        attr = {}
        for i in range(len(rows)):
            if (rows[i][0] not in attr):
                attr.update({rows[i][0]: []})
            attr[rows[i][0]].append(rows[i][1])
        return attr

    # returns a list of all the tables in progreSQL
    def getTableList (self):  # change to GetTableList
        # self.ConnectProgreSQL()
        # execute query
        # cur.execute("EXPLAIN ANALYZE select l_comment from lineitem WHERE l_shipmode ='AIR' ORDER BY l_tax")
        self.cur.execute("""SELECT table_name FROM information_schema.tables
               WHERE table_schema = 'public'""")
        rows = self.cur.fetchall()
        new = []
        for row in rows:
            new.append(row[0])
        return new

    # get JSON file from postgreSQL
    def GetJson (self, query, i):
        # print("Generating query plan for: " + query)
        status = True
        try:
            words = re.split("select", query, flags=re.IGNORECASE)
            # print("ckpt")
            # print(len(words), words[1])
            if(words[1] != ""):
                join_query = words[0] + "EXPLAIN (FORMAT JSON)"
                for x in words[1:]:
                    join_query = join_query + "SELECT" + x
            else:
                join_query = words[0]

            self.cur.execute(join_query)
            plan = self.cur.fetchall()

        except:
            status = False
            print("Failed to generate query plan execution!")
            self.ReInit_DB()
            return status
        finally:
            if status:
                output = json.dumps(plan, indent=4)
                # print("Generated query plan: " +
                #       output)
                with open('json.txt', 'w', newline='') as outfile:
                    outfile.writelines(output)
                return status

    def ExecuteQuery (self, query):
        self.cur.execute(query)
        rows = self.cur.fetchall()
        return rows

    # convert plan to text in list format
    def ConvertQueryToText (self, query, i):
        if self.GetJson(query,i) == True:
            explanation, plan, join_list, scan_list = PlanToText()
            if i == 1:
                self.qep1_plan = plan
                self.qep1 = [join_list,scan_list, plan]
                #print(self.qep1[0][1][1]['rightTable'])
            elif i == 2:
                self.qep2_plan = plan
                self.qep2 = [join_list,scan_list, plan]
            else:
                return True, ['Only allow QEP 1 and 2!']
            return True, explanation
        else:
            return False, ""

    def CompareQEPs(self):
        comparison_string_list = []
        # Check if there are 2 queries first
        if self.qep1 is None or self.qep2 is None:
            comparison_string_list.append("Error. Please enter 2 queries to begin comparison.")
            return comparison_string_list

        noJoinChanges = True
        noScanChanges = True
        QEP1joinlist = self.qep1[0]
        QEP1scanlist = self.qep1[1]
        QEP1root = self.qep1[2]
        QEP2joinlist = self.qep2[0]
        QEP2scanlist = self.qep2[1]
        QEP2root = self.qep2[2]
        # print('qep1 --> ', self.qep1)
        # print('qep2 --> ', self.qep2)

        # part 1: Changes in JOIN
        for x in QEP1joinlist:
            QEP1_parent = x[0]
            QEP1_leftchild = x[1]['leftTable']
            QEP1_rightchild = x[1]['rightTable']
            QEP1_leftChild_relation = None
            QEP1_leftChild_alias = None
            QEP1_leftChild_cond = None
            QEP1_leftChild_jointype = None
            QEP1_rightChild_relation = None
            QEP1_rightChild_alias = None
            QEP1_rightChild_cond = None
            QEP1_rightChild_jointype = None
            QEP1_join_output_cost = None
            QEP1_join_startup_cost = None
            # print("QEP 1: ")
            # print(x)
            for y in QEP2joinlist:
                QEP2_parent = y[0]
                QEP2_leftchild = y[1]['leftTable']
                QEP2_rightchild = y[1]['rightTable']
                # print("QEP2: ")
                # print(y)
                QEP2_leftChild_relation = None
                QEP2_leftChild_alias = None
                QEP2_leftChild_cond = None
                QEP2_leftChild_jointype = None
                QEP2_rightChild_relation = None
                QEP2_rightChild_alias = None
                QEP2_rightChild_cond = None
                QEP2_rightChild_jointype = None
                QEP2_join_output_cost = None
                QEP2_join_startup_cost = None

                #phase 1
                # Check if the left child of a JOIN contains a scan node that can provide 'relation name' and 'alias'
                # Otherwise, check if it contains a JOIN node
                # Otherwise, traverse tree to find the first SCAN or JOIN node
                # Try to match left scan node for both QEPs, if does not match, continue to next QEP2 node
                if 'Relation Name' in QEP1_leftchild:
                    QEP1_leftChild_relation = QEP1_leftchild['Relation Name']
                    if 'Alias' in QEP1_leftchild:
                        QEP1_leftChild_alias = QEP1_leftchild['Alias']
                        if 'Relation Name' in QEP2_leftchild:
                            QEP2_leftChild_relation = QEP2_leftchild['Relation Name']
                            if 'Alias' in QEP2_leftchild:
                                QEP2_leftChild_alias = QEP2_leftchild['Alias']
                                if QEP1_leftchild['Relation Name'] != QEP2_leftchild['Relation Name'] or QEP1_leftchild['Alias'] != QEP2_leftchild['Alias']:
                                    continue # go to next QEP2 join list to check for match since this left child does not match
                        #else QEP2's left child does not match QEP1's
                        else:
                            continue
                # Try to match left merge join nodes for both QEPs
                elif QEP1_leftchild['Node Type'] == 'Merge Join':
                    QEP1_leftChild_jointype = 'Merge Join'
                    QEP1_leftChild_cond = QEP1_leftchild['Merge Cond']
                    if QEP2_leftchild['Node Type'] == 'Merge Join':
                        QEP2_leftChild_jointype = 'Merge Join'
                        QEP2_leftChild_cond = QEP2_leftchild['Merge Cond']
                        if QEP1_leftChild_jointype != QEP2_leftChild_cond:
                            continue # go to next QEP2 join list to check for match since this left child does not match
                    # else QEP2's left child does not match QEP1's
                    else:
                        continue
                elif QEP1_leftchild['Node Type'] == 'Hash Join':
                    QEP1_leftChild_jointype = 'Hash Join'
                    QEP1_leftChild_cond = QEP1_leftchild['Hash Cond']
                    if QEP2_leftchild['Node Type'] == 'Hash Join':
                        QEP2_leftChild_jointype = 'Hash Join'
                        QEP2_leftChild_cond = QEP2_leftchild['Hash Cond']
                        if QEP1_leftChild_jointype != QEP2_leftChild_cond:
                            continue  # go to next QEP2 join list to check for match since this left child does not match
                    # else QEP2's left child does not match QEP1's
                    else:
                        continue
                elif QEP1_leftchild['Node Type'] == 'Nested Loop':
                    QEP1_leftChild_jointype = 'Nested Loop'
                    if QEP2_leftchild['Node Type'] == 'Nested Loop':
                        QEP2_leftChild_jointype = 'Nested Loop'
                    # else QEP2's left child does not match QEP1's
                    else:
                        continue
                else: # left child is none of the above, needs traversal to reach join or scan node
                    # else it is not a scan or join node, traverse tree until a scan or join node is reached
                    QEP1_leftChild_relation, QEP1_leftChild_alias, QEP1_leftChild_jointype, QEP1_leftChild_cond = self.TraverseTree(QEP1_leftchild)
                    # Check QEP2 type of node
                    if 'Relation Name' in QEP2_leftchild:
                        QEP2_leftChild_relation = QEP2_leftchild['Relation Name']
                        QEP2_leftChild_alias = QEP2_leftchild['Alias']
                    elif 'Join' in QEP2_leftchild:
                        QEP2_leftChild_jointype = QEP2_leftchild['Node Type']
                        if QEP2_leftChild_jointype != 'Merge Join':
                            QEP2_leftChild_cond = QEP2_leftchild['Merge Cond']
                        if QEP2_leftChild_jointype != 'Hash Join':
                            QEP2_leftChild_cond = QEP2_leftchild['Hash Cond']
                    else: # need to traverse QEP2 to reach a JOIN or SCAN node
                        QEP2_leftChild_relation, QEP2_leftChild_alias, QEP2_leftChild_jointype, QEP2_leftChild_cond = self.TraverseTree(QEP2_leftchild)
                    if QEP1_leftChild_relation is not None:
                            if QEP1_leftChild_relation == QEP2_leftChild_relation:
                                if QEP1_leftChild_alias != QEP2_leftChild_alias:
                                    continue # QEP2's left child does not match QEP1's
                            else:
                                # else QEP2's left child does not match QEP1's
                                continue
                    elif QEP1_leftChild_jointype is not None:
                        if QEP1_leftChild_jointype == QEP2_leftChild_jointype:
                            if QEP1_leftChild_jointype == 'Nested Loop':
                                print("")
                                #do nothing as nested loop do not need to check condition
                            elif QEP1_leftChild_cond != QEP2_leftChild_cond :
                                # else QEP2's left child does not match QEP1's
                                continue

                # Next, check for the right child node
                # the conditions will be the same as the left child node
                if 'Relation Name' in QEP1_rightchild:
                    QEP1_rightChild_relation = QEP1_rightchild['Relation Name']
                    if 'Alias' in QEP1_rightchild:
                        QEP1_rightChild_alias = QEP1_rightchild['Alias']
                        if 'Relation Name' in QEP2_rightchild:
                            QEP2_rightChild_relation = QEP2_rightchild['Relation Name']
                            if 'Alias' in QEP2_rightchild:
                                QEP2_rightChild_alias = QEP2_rightchild['Alias']
                                if QEP1_rightchild['Relation Name'] != QEP2_rightchild['Relation Name'] or QEP1_rightchild['Alias'] != QEP2_rightchild['Alias']:
                                    continue # go to next QEP2 join list to check for match since this right child does not match
                        #else QEP2's right child does not match QEP1's
                        else:
                            continue
                # Try to match right merge join nodes for both QEPs
                elif QEP1_rightchild['Node Type'] == 'Merge Join':
                    QEP1_rightChild_jointype = 'Merge Join'
                    QEP1_rightChild_cond = QEP1_rightchild['Merge Cond']
                    if QEP2_rightchild['Node Type'] == 'Merge Join':
                        QEP2_rightChild_jointype = 'Merge Join'
                        QEP2_rightChild_cond = QEP2_rightchild['Merge Cond']
                        if QEP1_rightChild_jointype != QEP2_rightChild_cond:
                            continue # go to next QEP2 join list to check for match since this right child does not match
                    # else QEP2's right child does not match QEP1's
                    else:
                        continue
                elif QEP1_rightchild['Node Type'] == 'Hash Join':
                    QEP1_rightChild_jointype = 'Hash Join'
                    QEP1_rightChild_cond = QEP1_rightchild['Hash Cond']
                    if QEP2_rightchild['Node Type'] == 'Hash Join':
                        QEP2_rightChild_jointype = 'Hash Join'
                        QEP2_rightChild_cond = QEP2_rightchild['Hash Cond']
                        if QEP1_rightChild_jointype != QEP2_rightChild_cond:
                            continue  # go to next QEP2 join list to check for match since this right child does not match
                    # else QEP2's right child does not match QEP1's
                    else:
                        continue
                elif QEP1_rightchild['Node Type'] == 'Nested Loop':
                    QEP1_rightChild_jointype = 'Nested Loop'
                    if QEP2_rightchild['Node Type'] == 'Nested Loop':
                        QEP2_rightChild_jointype = 'Nested Loop'
                    # else QEP2's right child does not match QEP1's
                    else:
                        continue
                else: # right child is none of the above, needs traversal to reach join or scan node
                    # else it is not a scan or join node, traverse tree until a scan or join node is reached
                    QEP1_rightChild_relation, QEP1_rightChild_alias, QEP1_rightChild_jointype, QEP1_rightChild_cond = self.TraverseTree(QEP1_rightchild)
                    # Check QEP2 type of node
                    if 'Relation Name' in QEP2_rightchild:
                        QEP2_rightChild_relation = QEP2_rightchild['Relation Name']
                        QEP2_rightChild_alias = QEP2_rightchild['Alias']
                    elif 'Join' in QEP2_rightchild:
                        QEP2_rightChild_jointype = QEP2_rightchild['Node Type']
                        if QEP2_rightChild_jointype != 'Merge Join':
                            QEP2_rightChild_cond = QEP2_rightchild['Merge Cond']
                        if QEP2_rightChild_jointype != 'Hash Join':
                            QEP2_rightChild_cond = QEP2_rightchild['Hash Cond']
                    else: # need to traverse QEP2 to reach a JOIN or SCAN node
                        QEP2_rightChild_relation, QEP2_rightChild_alias, QEP2_rightChild_jointype, QEP2_rightChild_cond = self.TraverseTree(QEP2_rightchild)
                    if QEP1_rightChild_relation is not None:
                            if QEP1_rightChild_relation == QEP2_rightChild_relation:
                                if QEP1_rightChild_alias != QEP2_rightChild_alias:
                                    continue # QEP2's right child does not match QEP1's
                            else:
                                # else QEP2's right child does not match QEP1's
                                continue
                    elif QEP1_rightChild_jointype is not None:
                        if QEP1_rightChild_jointype == QEP2_rightChild_jointype:
                            if QEP1_rightChild_jointype == 'Nested Loop':
                                print("")
                                #do nothing as nested loop do not need to check condition
                            elif QEP1_rightChild_cond != QEP2_rightChild_cond :
                                # else QEP2's right child does not match QEP1's
                                continue

                # phase 2
                # Check if QEP1 and QEP2's left and right child are the same, then check if the parent node JOIN is different
                # case 1: left child is a scan node and right child is a scan node
                if QEP1_leftChild_relation is not None and QEP2_leftChild_relation is not None:
                    if QEP1_rightChild_relation is not None and QEP2_rightChild_relation is not None:
                        if QEP1_leftChild_relation == QEP2_leftChild_relation:
                            if QEP1_leftChild_alias == QEP2_leftChild_alias:
                                if QEP1_rightChild_relation == QEP2_rightChild_relation:
                                    if QEP1_rightChild_alias == QEP2_rightChild_alias:
                                        if QEP1_parent['Node Type'] != QEP2_parent['Node Type']:
                                            noJoinChanges = False
                                            temp = "The type of join has changed from "+QEP1_parent['Node Type']+" in Query 1 to "+QEP2_parent['Node Type']+" in Query 2 for joining the relations "+QEP1_leftChild_relation+" "+QEP1_leftChild_alias+" and "+QEP1_rightChild_relation+" "+QEP1_rightChild_alias
                                            comparison_string_list.append(temp)
                                            comparison_string_list.append( self.CompareJoinNode(QEP1_parent['Node Type'], QEP2_parent['Node Type'],QEP1_parent,QEP2_parent) )
                                        # if both children of each QEP matches, find the Output cost of each QEP
                                        QEP1_join_output_cost = QEP1_parent['Total Cost'] - QEP1_parent['Startup Cost']
                                        QEP2_join_output_cost = QEP2_parent['Total Cost'] - QEP2_parent['Startup Cost']
                                        QEP1_join_startup_cost = QEP1_parent['Startup Cost']
                                        QEP2_join_startup_cost = QEP2_parent['Startup Cost']

                #case 2: left child is a scan node and right child is a join node
                if QEP1_rightChild_jointype is not None and QEP2_rightChild_jointype is not None:
                    if QEP1_rightChild_relation is not None and QEP2_rightChild_relation is not None:
                        if QEP1_leftChild_relation == QEP2_leftChild_relation:
                            if QEP1_leftChild_alias == QEP2_leftChild_alias:
                                if QEP1_rightChild_jointype == QEP2_rightChild_jointype:
                                    if QEP1_rightChild_cond == QEP2_rightChild_cond: #if the join type is nested loop, both values will be = None, so the condition will still pass
                                        if QEP1_parent['Node Type'] != QEP2_parent['Node Type']:
                                            noJoinChanges = False
                                            temp = "The type of join has changed from " + QEP1_parent['Node Type'] + " in Query 1 to " + QEP2_parent['Node Type'] + " in Query 2 for joining the relation " +QEP1_leftChild_relation+" "+QEP1_leftChild_alias+" with the "+QEP1_rightChild_jointype+" of 2 other relations"
                                            if 'Join' in QEP1_rightChild_jointype:
                                                temp += " under "+ QEP1_rightChild_cond
                                            comparison_string_list.append(temp)
                                            comparison_string_list.append( self.CompareJoinNode(QEP1_parent['Node Type'], QEP2_parent['Node Type'],QEP1_parent,QEP2_parent) )
                                        #if both children of each QEP matches, find the Output cost of each QEP
                                        QEP1_join_output_cost = QEP1_parent['Total Cost'] - QEP1_parent['Startup Cost']
                                        QEP2_join_output_cost = QEP2_parent['Total Cost'] - QEP2_parent['Startup Cost']
                                        QEP1_join_startup_cost = QEP1_parent['Startup Cost']
                                        QEP2_join_startup_cost = QEP2_parent['Startup Cost']

                # case 3: left child is a join node and right child is a scan node
                if QEP1_leftChild_jointype is not None and QEP2_leftChild_jointype is not None:
                    if QEP1_rightChild_relation is not None and QEP2_rightChild_relation is not None:
                        if QEP1_leftChild_jointype == QEP2_leftChild_jointype:
                            if QEP1_leftChild_cond == QEP2_leftChild_cond: #if the join type is nested loop, both values will be = None, so the condition will still pass
                                if QEP1_rightChild_relation == QEP2_rightChild_relation:
                                    if QEP1_rightChild_alias == QEP2_rightChild_alias:
                                        if QEP1_parent['Node Type'] != QEP2_parent['Node Type']:
                                            noJoinChanges = False
                                            temp = "The type of join has changed from " + QEP1_parent['Node Type'] + " in Query 1 to " + QEP2_parent['Node Type'] + " in Query 2 for joining " +QEP1_leftChild_jointype+" of 2 other relations"
                                            if 'Join' in QEP1_leftChild_jointype:
                                                temp += " under "+ QEP1_leftChild_cond
                                            temp += "and " + QEP1_rightChild_relation + " " + QEP1_rightChild_alias
                                            comparison_string_list.append(temp)
                                            comparison_string_list.append( self.CompareJoinNode(QEP1_parent['Node Type'], QEP2_parent['Node Type'],QEP1_parent,QEP2_parent) )
                                        # if both children of each QEP matches, find the Output cost of each QEP
                                        QEP1_join_output_cost = QEP1_parent['Total Cost'] - QEP1_parent['Startup Cost']
                                        QEP2_join_output_cost = QEP2_parent['Total Cost'] - QEP2_parent['Startup Cost']
                                        QEP1_join_startup_cost = QEP1_parent['Startup Cost']
                                        QEP2_join_startup_cost = QEP2_parent['Startup Cost']
                
                # Get left and right child details to print. Since QEPs will have same left and right child, only one set is needed
                QEP1printleftname,QEP1printleftdetail,QEP1printrightname,QEP1printrightdetail = self.getChildPrintDetails(QEP1_leftChild_relation,QEP1_leftChild_alias,QEP1_leftChild_jointype,QEP1_leftChild_cond,QEP1_rightChild_relation,QEP1_rightChild_alias,QEP1_rightChild_jointype,QEP1_rightChild_cond)

                # Generally output cost should be the same if they are the same nodes since it will return same number of tuples(since same results)
                if QEP1_join_output_cost != QEP2_join_output_cost:
                    noJoinChanges = False
                    temp = "The cost to emit all tuples for joining (Left child: "+QEP1printleftname+" "+QEP1printleftdetail+") and (Right child: "+QEP1printrightname+" "+QEP1printrightdetail+") has changed from " + str(QEP1_join_output_cost) +"(QEP1 node: "+QEP1_parent['Node Type'] +") to " + str(QEP2_join_output_cost)+"(QEP2 node: "+QEP2_parent['Node Type']+")"
                    comparison_string_list.append(temp)
                if QEP1_join_startup_cost != QEP2_join_startup_cost:
                    noJoinChanges = False
                    temp = "The startup cost for joining (Left child: "+QEP1printleftname+" "+QEP1printleftdetail+") and (Right child: "+QEP1printrightname+" "+QEP1printrightdetail+ ") has changed from " + str(QEP1_join_startup_cost) +"(QEP1 node: "+QEP1_parent['Node Type'] +") to " + str(QEP2_join_startup_cost)+"(QEP2 node: "+QEP2_parent['Node Type']+")"
                    comparison_string_list.append(temp)
                break  # stop looping through QEP2 since a match has already been found for a join of QEP1.
        # Part 2: changes in SCAN
        for x in QEP1scanlist:
            QEP1_scan_output_cost = None
            for y in QEP2scanlist:
                QEP1_scan_node = x
                QEP2_scan_node = y
                QEP2_scan_output_cost = None

                if QEP1_scan_node['Relation Name'] == QEP2_scan_node['Relation Name']:
                    if QEP1_scan_node['Alias'] == QEP2_scan_node['Alias']:
                        if QEP1_scan_node['Node Type'] != QEP2_scan_node['Node Type']:
                            noScanChanges = False
                            temp = "The type of Scan has changed from " + QEP1_scan_node['Node Type'] + " in Query 1 to " + QEP2_scan_node['Node Type'] + " in Query 2 for scanning the relation " + QEP1_scan_node['Relation Name'] + " " + QEP1_scan_node['Alias']
                            if 'Index' in QEP2_scan_node['Node Type']:
                                temp+= " using index "
                            comparison_string_list.append(temp)
                            # add explaination for why the scan node has changed.
                            if ((QEP1_scan_node['Node Type'] == 'Index Scan' and QEP2_scan_node['Node Type'] == 'Seq Scan')):
                                comparison_string_list.append(
                                    "Seq scan is used in the second query as the SELECT returns more than 5-10% of all the rows in the table")
                            elif (QEP1_scan_node['Node Type'] == 'Seq Scan' and QEP2_scan_node['Node Type'] == 'Index Scan'):
                                comparison_string_list.append(
                                    "Index scan is used when the matched items are the least common. ")
                            elif (QEP2_scan_node['Node Type'] == 'Bitmap Heap Scan'):
                                comparison_string_list.append(
                                    " Bitmap Heap Scan reads through the bitmap to get heap data corresponding to stored page number and offset.")
                            #elif (QEP2_scan_node['Node Type'].contains('Bitmap Index Scan')):
                             #   comparison_string_list.append(" Bitmap index scan is used to avoid unneccessary heap blocks reads (or hits if there is a hot cache).")

                        QEP1_scan_output_cost = QEP1_scan_node['Total Cost'] - QEP1_scan_node['Startup Cost']
                        QEP2_scan_output_cost = QEP2_scan_node['Total Cost'] - QEP2_scan_node['Startup Cost']
                        #Generally output cost should be the same if they are the same nodes since it will return same number of tuples(since same results)
                        if QEP1_scan_output_cost != QEP2_scan_output_cost:
                            noScanChanges = False
                            temp = "The cost to emit all tuples for "+QEP1_scan_node['Relation Name']+" "+ QEP1_scan_node['Alias'] +" has changed from "+str(QEP1_scan_output_cost)+"(QEP1 node: "+QEP1_scan_node['Node Type']+") to "+ str(QEP2_scan_output_cost)+"(QEP2 node: "+QEP2_scan_node['Node Type']+")"
                            comparison_string_list.append(temp)
                        if QEP1_scan_node['Startup Cost'] != QEP2_scan_node['Startup Cost']:
                            noScanChanges = False
                            temp = "The startup cost for "+QEP1_scan_node['Relation Name']+" "+ QEP1_scan_node['Alias'] +" has changed from " + str(QEP1_scan_node['Startup Cost']) +"(QEP1 node: "+QEP1_scan_node['Node Type']+ ") to " + str(QEP2_scan_node['Startup Cost'])+"(QEP2 node: "+QEP2_scan_node['Node Type']+")"
                            comparison_string_list.append(temp)

        # Part 3: final touches
        if noJoinChanges:
            comparison_string_list.append("No JOIN algorithms changes detected between Query 1 and Query 2.")

        if noScanChanges:
            comparison_string_list.append("No SCAN algorithms changes detected between Query 1 and Query 2.")

        if not noJoinChanges or not noScanChanges: # if there is at least a JOIN or SCAN change
            comparison_string_list.append("Conclusion: The total cost of Query 1 changed from "+ str(QEP1root['Total Cost'])+" to "+str(QEP2root['Total Cost'])+ " in Query 2")

        return comparison_string_list

    #traverse tree to find the first node that will return relation name and alias
    def TraverseTree(self,parent_node):

        q = queue.Queue()
        relation_name = None
        alias_name = None

        q.put(parent_node)
        while not q.empty():
            current_node = q.get()
            # print(current_node)
            if 'Plans' in current_node:
                leftSub = (current_node['Plans'][0])

                # For cases where the child is a join node, return the join type
                if 'Join' in leftSub['Node Type'] or 'Loop' in leftSub['Node Type']:
                    join_type = leftSub['Node Type']
                    if join_type == 'Hash Join':
                        return None,None,join_type,leftSub['Hash Cond']
                    elif join_type == 'Merge Join':
                        return None,None,join_type,leftSub['Merge Cond']
                    else: #else it will be nested loop join
                        return None,None,join_type,None

                if 'Relation Name' in leftSub:
                    relation_name = leftSub['Relation Name']
                    if 'Alias' in leftSub:
                        alias_name = leftSub['Alias']

                for item in current_node['Plans']:
                    # push child plans into queue
                    q.put(item)
        return relation_name,alias_name,None,None

    def getChildPrintDetails(self,QEP1_leftChild_relation,QEP1_leftChild_alias,QEP1_leftChild_jointype,QEP1_leftChild_cond,QEP1_rightChild_relation,QEP1_rightChild_alias,QEP1_rightChild_jointype,QEP1_rightChild_cond):
        QEP1printleftname = None
        QEP1printleftdetail = None
        QEP1printrightname = None
        QEP1printrightdetail = None

        if QEP1_leftChild_relation is not None:
            QEP1printleftname = QEP1_leftChild_relation
            if QEP1_leftChild_alias is not None:
                QEP1printleftdetail = QEP1_leftChild_alias
        elif QEP1_leftChild_jointype is not None:
            QEP1printleftname = QEP1_leftChild_jointype
            if QEP1_leftChild_cond is not None:
                QEP1printleftdetail = QEP1_leftChild_cond

        if QEP1_rightChild_relation is not None:
            QEP1printrightname = QEP1_rightChild_relation
            if QEP1_rightChild_alias is not None:
                QEP1printrightdetail = QEP1_rightChild_alias
        elif QEP1_rightChild_jointype is not None:
            QEP1printrightname = QEP1_rightChild_jointype
            if QEP1_rightChild_cond is not None:
                QEP1printrightdetail = QEP1_rightChild_cond


        return QEP1printleftname,QEP1printleftdetail,QEP1printrightname,QEP1printrightdetail

    # Must call this after the user log out or close app
    def CloseConnection (self):
        # closing database connection.
        if (self.con):
            self.cur.close()
            self.con.close()
            return "PostgreSQL connection is closed."
        return "No connection was established in the first place!"

    def TraverseForIndex(self, current):
        if 'Plans' in current:
            # traverse all left nodes
            if 'Index Scan' == current['Plans'][0]['Node Type']:
                return True
            else:
                status = self.TraverseForIndex()
            # status == True, index scan found, skip traverse to right child
            # status == False, index scan not found
            # if joins found, traverse right child after backtracking from left child
            if status == False and len(current['Plans']) == 2:
                if 'Index Scan' == current['Plans'][1]['Node Type']:
                    return True
                else:
                    self.TraverseForIndex()
        else:
            return False

    def TraverseForLimit(self, current):
        if 'Plans' in current:
            # traverse all left nodes
            if 'Limit' == current['Plans'][0]['Node Type']:
                return True
            else:
                status = self.TraverseForIndex(current['Plans'][0])
            # status == True, index scan found, skip traverse to right child
            # status == False, index scan not found
            # if joins found, traverse right child after backtracking from left child
            if status == False and len(current['Plans']) == 2:
                if 'Limit' == current['Plans'][1]['Node Type']:
                    return True
                else:
                    self.TraverseForIndex(current['Plans'][1])
        else:
            return False

    def CompareJoinNode(self, qep1_join_node, qep2_join_node, qep1, qep2):
        # check for input rows
        qep1_left_rows = qep1['Plans'][0]['Plan Rows']
        qep1_right_rows = qep1['Plans'][0]['Plan Rows']
        qep2_left_rows = qep2['Plans'][1]['Plan Rows']
        qep2_right_rows = qep2['Plans'][1]['Plan Rows']

        smaller_relation = False
        if qep1_left_rows > qep2_left_rows:
            string = 'left input relation only has ' + qep1_right_rows + ' rows now, '
            smaller_relation = True
        elif qep1_right_rows > qep2_right_rows:
            string = 'right input relation only has ' + qep2_right_rows + ' rows now, '
            smaller_relation = True

        if 'Filter' in qep2:
            join_filter = qep2['Filter Join']
            join_filter = join_filter.split()
            for i in range(len(join_filter)):
                join_filter[i] = join_filter[i].replace('(', '').replace(')', '')
            left_attr = join_filter[0]
            right_attr = join_filter[2]

        limit_in_qep2 = ''
        if self.TraverseForLimit(qep2_join_node):
            limit_in_qep2 = 'as there is a LIMIT in the ordering to reduce the number of tuples in the input relation, '

        # explains why the index change
        if qep1_join_node != qep2_join_node:
            if 'Merge' in qep2_join_node:
                # regardless what the previous join type is
                temp = qep2_join_node + ' is used in QEP2 because ' + \
                       'the attributes ' + left_attr + ' and ' + right_attr + \
                       ' to be joined are sorted in Q2 and the relations are joined based on equality check, =, ' \
                       'thus reducing the join cost if Merge Join is used.'

            elif 'Hash' in qep2_join_node:
                temp = qep2_join_node + ' is used in QEP2 because ' + \
                       'the relations are joined based on the equality check, =,' \
                       ' and both relations are not sorted on the join attribute, ' \
                       'thus reducing the join cost if Hash Join is used.'

            elif 'Nested' in qep2_join_node:
                if smaller_relation:
                    temp = qep2_join_node + ' is used in QEP2 because ' + \
                           string + limit_in_qep2 + \
                           'allowing it to fit entirely in the main memory, hence decreasing the cost.'
                else:
                    temp = qep2_join_node + ' is used in QEP2 because ' + \
                           'the input relations are not sorted and ' \
                           'the filter condition is based on inequality or range check, ' + \
                           'resulting the size of the output tuples to be a larger percentage of the total tuples joined, ' \
                           'thus Nested Loop Join will work best in this scenario.'

            else:
                # improvements not considered
                temp = 'Sorry but this improvement of join is not considered, ' \
                       'please enhance the algorithm and include this improvement, ' + \
                       qep1_join_node + ' changed to ' + qep2_join_node + ',' \
                                                                          'my apologies for the inconvenience caused.'
            return (temp)
        return


    def GetPlan(self, i):
        if i == 1:
            return self.qep1_plan
        elif i == 2:
            return self.qep2_plan
        return -1

def init_comm ():
    comm = Communicator()
    return comm

# if __name__ == '__main__':
#     comm = Communicator()
#     comm.ConnectProgreSQL()
#     comm.GetAttrDict()
#     comm.CloseConnection()
