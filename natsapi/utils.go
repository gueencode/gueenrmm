package api

import (
	"encoding/json"
	"errors"
	"fmt"
	"io/ioutil"
	"time"

	grmm "github.com/gueencode/grmm-shared"
	"github.com/jmoiron/sqlx"
	_ "github.com/lib/pq"
	nats "github.com/nats-io/nats.go"
)

func setupNatsOptions(key string) []nats.Option {
	opts := []nats.Option{
		nats.Name("gueenrmm"),
		nats.UserInfo("gueenrmm", key),
		nats.ReconnectWait(time.Second * 2),
		nats.RetryOnFailedConnect(true),
		nats.MaxReconnects(-1),
		nats.ReconnectBufSize(-1),
	}
	return opts
}

func GetConfig(cfg string) (db *sqlx.DB, r DjangoConfig, err error) {
	if cfg == "" {
		cfg = "/rmm/api/gueenrmm/nats-api.conf"
		if !grmm.FileExists(cfg) {
			err = errors.New("unable to find config file")
			return
		}
	}

	jret, _ := ioutil.ReadFile(cfg)
	err = json.Unmarshal(jret, &r)
	if err != nil {
		return
	}

	psqlInfo := fmt.Sprintf("host=%s port=%d user=%s "+
		"password=%s dbname=%s sslmode=disable",
		r.Host, r.Port, r.User, r.Pass, r.DBName)

	db, err = sqlx.Connect("postgres", psqlInfo)
	if err != nil {
		return
	}
	db.SetMaxOpenConns(20)
	return
}
