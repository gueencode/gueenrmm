package api

import (
	"encoding/json"
	"reflect"
	"runtime"
	"time"

	grmm "github.com/gueencode/grmm-shared"
	_ "github.com/lib/pq"
	nats "github.com/nats-io/nats.go"
	"github.com/sirupsen/logrus"
	"github.com/ugorji/go/codec"
)

func Svc(logger *logrus.Logger, cfg string) {
	logger.Debugln("Starting Svc()")
	db, r, err := GetConfig(cfg)
	if err != nil {
		logger.Fatalln(err)
	}

	opts := setupNatsOptions(r.Key)
	nc, err := nats.Connect(r.NatsURL, opts...)
	if err != nil {
		logger.Fatalln(err)
	}

	nc.Subscribe("*", func(msg *nats.Msg) {
		var mh codec.MsgpackHandle
		mh.MapType = reflect.TypeOf(map[string]interface{}(nil))
		mh.RawToString = true
		dec := codec.NewDecoderBytes(msg.Data, &mh)

		switch msg.Reply {
		case "agent-hello":
			go func() {
				var p grmm.CheckInNats
				if err := dec.Decode(&p); err == nil {
					loc, _ := time.LoadLocation("UTC")
					now := time.Now().In(loc)
					logger.Debugln("Hello", p, now)
					stmt := `
					UPDATE agents_agent
					SET last_seen=$1, version=$2
					WHERE agents_agent.agent_id=$3;
					`

					_, err = db.Exec(stmt, now, p.Version, p.Agentid)
					if err != nil {
						logger.Errorln(err)
					}
				}
			}()

		case "agent-publicip":
			go func() {
				var p grmm.PublicIPNats
				if err := dec.Decode(&p); err == nil {
					logger.Debugln("Public IP", p)
					stmt := `
					UPDATE agents_agent SET public_ip=$1 WHERE agents_agent.agent_id=$2;`
					_, err = db.Exec(stmt, p.PublicIP, p.Agentid)
					if err != nil {
						logger.Errorln(err)
					}
				}
			}()

		case "agent-agentinfo":
			go func() {
				var r grmm.AgentInfoNats
				if err := dec.Decode(&r); err == nil {
					stmt := `
						UPDATE agents_agent
						SET hostname=$1, operating_system=$2,
						plat=$3, total_ram=$4, boot_time=$5, needs_reboot=$6, logged_in_username=$7
						WHERE agents_agent.agent_id=$8;`

					logger.Debugln("Info", r)
					_, err = db.Exec(stmt, r.Hostname, r.OS, r.Platform, r.TotalRAM, r.BootTime, r.RebootNeeded, r.Username, r.Agentid)
					if err != nil {
						logger.Errorln(err)
					}

					if r.Username != "None" {
						stmt = `UPDATE agents_agent SET last_logged_in_user=$1 WHERE agents_agent.agent_id=$2;`
						logger.Debugln("Updating last logged in user:", r.Username)
						_, err = db.Exec(stmt, r.Username, r.Agentid)
						if err != nil {
							logger.Errorln(err)
						}
					}
				}
			}()

		case "agent-disks":
			go func() {
				var r grmm.WinDisksNats
				if err := dec.Decode(&r); err == nil {
					logger.Debugln("Disks", r)
					b, err := json.Marshal(r.Disks)
					if err != nil {
						logger.Errorln(err)
						return
					}
					stmt := `
					UPDATE agents_agent SET disks=$1 WHERE agents_agent.agent_id=$2;`

					_, err = db.Exec(stmt, b, r.Agentid)
					if err != nil {
						logger.Errorln(err)
					}
				}
			}()

		case "agent-winsvc":
			go func() {
				var r grmm.WinSvcNats
				if err := dec.Decode(&r); err == nil {
					logger.Debugln("WinSvc", r)
					b, err := json.Marshal(r.WinSvcs)
					if err != nil {
						logger.Errorln(err)
						return
					}

					stmt := `
					UPDATE agents_agent SET services=$1 WHERE agents_agent.agent_id=$2;`

					_, err = db.Exec(stmt, b, r.Agentid)
					if err != nil {
						logger.Errorln(err)
					}
				}
			}()

		case "agent-wmi":
			go func() {
				var r grmm.WinWMINats
				if err := dec.Decode(&r); err == nil {
					logger.Debugln("WMI", r)
					b, err := json.Marshal(r.WMI)
					if err != nil {
						logger.Errorln(err)
						return
					}
					stmt := `
					UPDATE agents_agent SET wmi_detail=$1 WHERE agents_agent.agent_id=$2;`

					_, err = db.Exec(stmt, b, r.Agentid)
					if err != nil {
						logger.Errorln(err)
					}
				}
			}()
		}
	})

	nc.Flush()

	if err := nc.LastError(); err != nil {
		logger.Fatalln(err)
	}
	runtime.Goexit()
}
