using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class MainMenuController : MonoBehaviour
{
    public GameObject m_MainManu;
    public GameObject m_Theory;
    public GameObject m_Quiz;
    public GameObject m_Modeling;
    public GameObject m_Grabbing;
    public GameObject m_Kidney;

    public void Theory_btn_clicked()
    {
        m_MainManu.SetActive(false);
        m_Theory.SetActive(true);
    }
    public void Theory_back_clicked()
    {
        m_MainManu.SetActive(true);
        m_Theory.SetActive(false);
    }
    public void Quiz_btn_clicked()
    {
        m_MainManu.SetActive(false);
        m_Quiz.SetActive(true);
    }
    public void Quiz_back_clicked()
    {
        m_MainManu.SetActive(true);
        m_Quiz.SetActive(false);
    }
    public void Modeling_btn_clicked()
    {
        m_MainManu.SetActive(false);

        Renderer rend = m_Kidney.GetComponent<Renderer>();
        rend.enabled = true;
    }
    public void Modeling_back_clicked()
    {
        m_MainManu.SetActive(true);
        m_Modeling.SetActive(false);
    }
    public void Grabbing_btn_clicked()
    {
        m_MainManu.SetActive(false);
        m_Grabbing.SetActive(true);
    }
    public void Grabbing_back_clicked()
    {
        m_MainManu.SetActive(true);
        m_Grabbing.SetActive(false);
    }
}
