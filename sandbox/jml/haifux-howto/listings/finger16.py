# Read from file, announce on the web, irc
from twisted.internet import protocol, reactor, defer, app
from twisted.protocols import basic, irc
from twisted.web import resource, server, static
import cgi
class FingerProtocol(basic.LineReceiver):
    def lineReceived(self, user):
        self.factory.getUser(user
        ).addErrback(lambda _: "Internal error in server"
        ).addCallback(lambda m:
            (self.transport.write(m+"\r\n"),self.transport.loseConnection()))
class FingerSetterProtocol(basic.LineReceiver):
      def connectionMade(self): self.lines = []
      def lineReceived(self, line): self.lines.append(line)
      def connectionLost(self): self.factory.setUser(*self.lines)
class IRCReplyBot(irc.IRCClient):
    def connectionMade(self):
        self.nickname = self.factory.nickname
        irc.IRCClient.connectionMade(self)
    def privmsg(self, user, channel, msg):
        if user.lower() == channel.lower():
            self.factory.getUser(msg
            ).addErrback(lambda _: "Internal error in server"
            ).addCallback(lambda m: self.msg(user, m))
class FingerService(app.ApplicationService):
      def __init__(self, file, *args, **kwargs):
          app.ApplicationService.__init__(self, *args, **kwargs)
          self.file = file
      def startService(self):
          app.ApplicationService.startService(self)
          self._read()
      def _read(self):
          self.users = {}
          for line in file(self.file):
              user, status = line.split(':', 1)
              self.users[user] = status
          self.call = reactor.callLater(30, self._read)
      def stopService(self):
          app.ApplicationService.stopService(self)
          self.call.cancel()
      def getUser(self, user):
          return defer.succeed(self.users.get(u, "No such user"))
      def getFingerFactory(self):
          f = protocol.ServerFactory()
          f.protocol, f.getUser = FingerProtocol, self.getUser
          return f
      def getResource(self):
          r = resource.Resource()
          r.getChild = (lambda path, request:
           static.Data('text/html',
            '<h1>%s</h1><p>%s</p>' %
              tuple(map(cgi.escape,
                        [path,self.users.get(path, "No such user")]))))
      def getIRCBot(self, nickname):
          f = protocol.ReconnectingClientFactory()
          f.protocol,f.nickname,f.getUser = IRCReplyBot,nickname,self.getUser
          return f
application = app.Application('finger', uid=1, gid=1)
f = FingerService('/etc/users', application, 'finger')
application.listenTCP(79, f.getFingerFactory())
application.listenTCP(80, server.Site(f.getResource()))
application.connectTCP('irc.freenode.org', 6667, f.getIRCBot('finger-bot'))
