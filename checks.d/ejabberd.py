# Datadog Agent Check Plugin for Ejabberd
# debug for:
# sudo -u dd-agent dd-agent check ejabberd

from checks import AgentCheck
import xmlrpclib

class EjabberdCheck(AgentCheck):
    SERVICE_CHECK_NAME = 'ejabberd.is_ok'

    def __init__(self, name, init_config, agentConfig, instances=None):
        AgentCheck.__init__(self, name, init_config, agentConfig, instances)

    def check(self, instance):
        verbose = self.init_config.get('verbose', False)
        server = xmlrpclib.ServerProxy(instance['url'], verbose=verbose);
        auth = {'user': instance['user'], 'server': instance['server'], 'password': instance['password']}
        try:
            res = server.stats_extra(auth, {'host': 'localhost'})
            for stat in res['stats']:
                # bit of hackery to get the stat out
                vals = stat['stat']
                # vals = '{"[counter|gauge]", "sys.nProcs",1550}'
                # Strip off brackets
                vals = vals[1:-1]

                typ, key, val = vals.split(",")
                # key = "sys.nProcs"
                # val = 1550
                key = key.replace('"', '')
                typ = typ.replace('"', '')
                try:
                    val = float(val)
                except:
                    pass

                # OK, type, key and val now sanitized
                print typ, key, val

                if typ == "gauge":
                    self.gauge("ejabberd.%s" % key, val)
                else:
                    self.count("ejabberd.%s" % key, val)

            self.service_check(self.SERVICE_CHECK_NAME, AgentCheck.OK)

        except Exception as e:
            self.service_check(self.SERVICE_CHECK_NAME, AgentCheck.CRITICAL,
                               message="Unable to get ejabberd stats: %s"
                               % str(e))
            pass
